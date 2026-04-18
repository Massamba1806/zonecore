import psycopg2
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from shapely.ops import unary_union
import numpy as np
from sqlalchemy import create_engine

print("🔌 Connexion PostGIS...")
conn = psycopg2.connect(
    host="127.0.0.1", port=5432,
    dbname="zonecore", user="postgres",
    password="Khodia1571@"
)
engine = create_engine(
    "postgresql+psycopg2://",
    creator=lambda: psycopg2.connect(
        host="127.0.0.1", port=5432,
        dbname="zonecore", user="postgres",
        password="Khodia1571@"
    )
)
print("✅ Connexion OK !")

STORE_LAT = 50.6292
STORE_LON = 3.0573

# ── Cercle classique 10km ────────────────────
print("\n⭕ Génération cercle classique 10km...")
store_point = gpd.GeoDataFrame(
    [{"geometry": Point(STORE_LON, STORE_LAT)}],
    crs="EPSG:4326"
).to_crs(epsg=2154)

cercle_10km = store_point.copy()
cercle_10km["geometry"] = store_point.buffer(10000)
cercle_10km = cercle_10km.to_crs(epsg=4326)
cercle_10km["type"] = "Cercle classique 10 km"
print("✅ Cercle 10km généré")

# ── Cercle classique 20km ────────────────────
cercle_20km = store_point.copy()
cercle_20km["geometry"] = store_point.buffer(20000)
cercle_20km = cercle_20km.to_crs(epsg=4326)
cercle_20km["type"] = "Cercle classique 20 km"
print("✅ Cercle 20km généré")

# ── Zone réelle — convex hull des clients ────
print("\n🗺️  Génération zone réelle par cluster...")
query = """
    SELECT
    cluster_dbscan,
    longitude,
    latitude,
    geometry
FROM raw_data.clients
WHERE cluster_dbscan != -1
AND geometry IS NOT NULL
AND ST_Distance(
    ST_Transform(geometry, 2154),
    ST_Transform(ST_SetSRID(ST_MakePoint(3.0573, 50.6292), 4326), 2154)
) < 35000;
"""
df = pd.read_sql(query, conn)
gdf_clients = gpd.GeoDataFrame(
    df,
    geometry=gpd.GeoSeries.from_wkb(df["geometry"]),
    crs="EPSG:4326"
)

# Zone réelle globale — convex hull de tous les clients
gdf_clients_proj = gdf_clients.to_crs(epsg=2154)
zone_buffer = unary_union(gdf_clients_proj.geometry).buffer(2000)
zone_reelle_global = gpd.GeoDataFrame(
    [{"geometry": zone_buffer}],
    crs="EPSG:2154"
).to_crs(epsg=4326)
zone_reelle_global["type"] = "Zone réelle globale"
print("✅ Zone réelle globale générée")

# Zone réelle par cluster
zones_clusters = []
NOMS = {
    0: "Famille périurbaine",
    1: "Suburban voiture",
    2: "Étudiant vélo",
    3: "Urbain transport",
    4: "Urbain proche"
}
for cluster_id, group in gdf_clients.groupby("cluster_dbscan"):
    if len(group) < 5:
        continue
    group_proj = group.to_crs(epsg=2154)
    hull = unary_union(group_proj.geometry).buffer(1500)
    group_temp = gpd.GeoDataFrame([{"geometry": hull}], crs="EPSG:2154").to_crs(epsg=4326)
    hull = group_temp.geometry.values[0]
    zones_clusters.append({
        "cluster_id": cluster_id,
        "nom":        NOMS.get(cluster_id, f"Cluster {cluster_id}"),
        "nb_clients": len(group),
        "geometry":   hull
    })
    print(f"   ✅ Cluster {cluster_id} — {NOMS.get(cluster_id)} ({len(group)} clients)")

gdf_zones = gpd.GeoDataFrame(zones_clusters, crs="EPSG:4326")

# ── Sauvegarde ───────────────────────────────
cercle_10km.to_file("data/exports/cercle_10km.geojson",       driver="GeoJSON")
cercle_20km.to_file("data/exports/cercle_20km.geojson",       driver="GeoJSON")
zone_reelle_global.to_file("data/exports/zone_reelle.geojson", driver="GeoJSON")
gdf_zones.to_file("data/exports/zones_clusters.geojson",      driver="GeoJSON")

print("\n💾 Fichiers sauvegardés :")
print("   data/exports/cercle_10km.geojson")
print("   data/exports/cercle_20km.geojson")
print("   data/exports/zone_reelle.geojson")
print("   data/exports/zones_clusters.geojson")

# ── Stats comparaison ────────────────────────
print("\n📊 Comparaison surfaces :")
cercle_10_m2 = store_point.buffer(10000).area.values[0]
zone_reelle_m2 = gpd.GeoDataFrame(
    [{"geometry": unary_union(gdf_clients.geometry).convex_hull}],
    crs="EPSG:4326"
).to_crs(epsg=2154).area.values[0]

print(f"   Cercle 10km    : {cercle_10_m2/1e6:.0f} km²")
print(f"   Zone réelle    : {zone_reelle_m2/1e6:.0f} km²")
print(f"   Différence     : {abs(cercle_10_m2 - zone_reelle_m2)/1e6:.0f} km²")

conn.close()
print("\n🎉 Terminé !")