import requests
import geopandas as gpd
import pandas as pd
import psycopg2
import folium
import json
import time
from shapely.geometry import shape
from sqlalchemy import create_engine

# ── Configuration ────────────────────────────
ORS_API_KEY = None
# Charge depuis .env
from pathlib import Path
from dotenv import load_dotenv
import os
load_dotenv(Path(__file__).parent.parent / ".env")
ORS_API_KEY = os.getenv("ORS_API_KEY")

print(f"🔑 Clé API : {ORS_API_KEY[:8]}...")

# ── Connexion PostGIS ────────────────────────
print("🔌 Connexion PostGIS...")
conn = psycopg2.connect(
    host="127.0.0.1", port=5432,
    dbname="zonecore", user="postgres",
    password="Khodia1571@"
)
print("✅ Connexion OK !")

# ── Paramètres isochrones par cluster ────────
ISOCHRONES_CONFIG = {
    0: {"profile": "driving-car",    "ranges": [600, 1200, 1800]},  # 10,20,30 min
    1: {"profile": "driving-car",    "ranges": [900, 1800]},         # 15,30 min
    2: {"profile": "cycling-regular","ranges": [600, 1200]},         # 10,20 min
    3: {"profile": "driving-car",    "ranges": [900, 1800]},         # 15,30 min
    4: {"profile": "foot-walking",   "ranges": [300, 600, 900]},     # 5,10,15 min
}

STORE_LAT = 50.6292
STORE_LON = 3.0573

def get_isochrone(lon, lat, profile, ranges):
    """
    Appelle l'API OpenRouteService pour générer une isochrone.
    """
    url = "https://api.openrouteservice.org/v2/isochrones/" + profile
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type":  "application/json"
    }
    body = {
        "locations":       [[lon, lat]],
        "range":           ranges,
        "range_type":      "time",
        "smoothing":       0.5,
    }
    try:
        r = requests.post(url, headers=headers, json=body, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"   ⚠️  Erreur ORS : {e}")
        return None

# ── Génère les isochrones ────────────────────
print("\n🗺️  Génération des isochrones...")
all_isochrones = []

for cluster_id, config in ISOCHRONES_CONFIG.items():
    print(f"\n  ▸ Cluster {cluster_id} — {config['profile']}")
    print(f"    Ranges : {[r//60 for r in config['ranges']]} minutes")

    data = get_isochrone(
        STORE_LON, STORE_LAT,
        config["profile"],
        config["ranges"]
    )

    if data and "features" in data:
        for feature in data["features"]:
            props    = feature["properties"]
            geometry = shape(feature["geometry"])
            duree    = props.get("value", 0) // 60

            all_isochrones.append({
                "cluster_id": cluster_id,
                "profile":    config["profile"],
                "duree_min":  duree,
                "geometry":   geometry
            })
            print(f"    ✅ Isochrone {duree} min générée")
    else:
        print(f"    ❌ Échec pour cluster {cluster_id}")

    # Respecte la limite API (40 req/min)
    time.sleep(2)

# ── Convertit en GeoDataFrame ────────────────
print(f"\n📊 {len(all_isochrones)} isochrones générées au total")
gdf_iso = gpd.GeoDataFrame(all_isochrones, crs="EPSG:4326")

# ── Sauvegarde GeoJSON ───────────────────────
gdf_iso.to_file("data/exports/isochrones.geojson", driver="GeoJSON")
print("💾 GeoJSON sauvegardé : data/exports/isochrones.geojson")

# ── Carte interactive ────────────────────────
print("\n🗺️  Génération de la carte...")

COULEURS = {
    0: "#E74C3C",
    1: "#3498DB",
    2: "#2ECC71",
    3: "#F39C12",
    4: "#9B59B6",
}

NOMS = {
    0: "Cluster 0 — Famille (voiture)",
    1: "Cluster 1 — Suburban (voiture)",
    2: "Cluster 2 — Étudiant (vélo)",
    3: "Cluster 3 — Urbain (transport)",
    4: "Cluster 4 — Urbain (marche)",
}

carte = folium.Map(
    location=[STORE_LAT, STORE_LON],
    zoom_start=12,
    tiles="CartoDB positron"
)

# Magasin
folium.Marker(
    location=[STORE_LAT, STORE_LON],
    popup="🏪 Decathlon Lille Nord",
    icon=folium.Icon(color="red", icon="shopping-cart", prefix="fa")
).add_to(carte)

# Isochrones par cluster
for cluster_id in sorted(gdf_iso["cluster_id"].unique()):
    groupe = folium.FeatureGroup(name=NOMS[cluster_id])
    subset = gdf_iso[gdf_iso["cluster_id"] == cluster_id].sort_values(
        "duree_min", ascending=False
    )

    for _, row in subset.iterrows():
        folium.GeoJson(
            row.geometry.__geo_interface__,
            style_function=lambda x, c=COULEURS[cluster_id], d=row.duree_min: {
                "fillColor":   c,
                "color":       c,
                "weight":      2,
                "fillOpacity": 0.15,
            },
            tooltip=f"{NOMS[cluster_id]} — {row.duree_min} min"
        ).add_to(groupe)

    groupe.add_to(carte)

folium.LayerControl(collapsed=False).add_to(carte)

output = "data/exports/carte_isochrones.html"
carte.save(output)
print(f"✅ Carte sauvegardée : {output}")
print("👉 Ouvre ce fichier dans ton navigateur !")

conn.close()
print("\n🎉 Isochrones terminées avec succès !")