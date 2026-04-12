import psycopg2
import geopandas as gpd
import pandas as pd
import folium
import requests
import os
from pathlib import Path

print("🚀 Calcul du taux de pénétration par IRIS...")

# ── Connexion ────────────────────────────────
conn = psycopg2.connect(
    host="127.0.0.1", port=5432,
    dbname="zonecore", user="postgres",
    password="Khodia1571@"
)
cur = conn.cursor()
print("✅ Connexion PostGIS OK !")

# ── Télécharge les données de population ─────
print("\n📥 Téléchargement données population INSEE...")
url = "https://data.opendatasoft.com/api/explore/v2.1/catalog/datasets/population-iris-2019@public/exports/csv?lang=fr&timezone=Europe%2FParis&use_labels=true&delimiter=%3B"

try:
    r = requests.get(url, timeout=30)
    if r.status_code == 200:
        with open("data/raw/population_iris.csv", "wb") as f:
            f.write(r.content)
        print("✅ Données population téléchargées !")
    else:
        print(f"⚠️  API status {r.status_code} — on utilise une population estimée")
except:
    print("⚠️  Téléchargement échoué — on utilise une population estimée")

# ── Calcul du taux de pénétration ────────────
print("\n📊 Calcul du taux de pénétration...")
cur.execute("""
    SELECT
        i.iris_code,
        i.nom_iris,
        i.commune,
        COUNT(c.client_id)                          as nb_clients,
        COUNT(c.client_id) * 1000.0 / NULLIF(50, 0) as taux_penetration,
        ROUND(AVG(c.panier_moyen)::numeric, 2)       as panier_moyen,
        ROUND(AVG(c.frequence_achat)::numeric, 1)    as freq_moyenne,
        i.geometry
    FROM raw_data.iris i
    LEFT JOIN raw_data.clients c ON c.iris_code = i.iris_code
    GROUP BY i.iris_code, i.nom_iris, i.commune, i.geometry
    ORDER BY nb_clients DESC;
""")

rows = cur.fetchall()
print(f"✅ {len(rows)} IRIS analysés")

# ── Crée le GeoDataFrame ─────────────────────
from shapely import wkb
import binascii

data = []
for row in rows:
    geom = wkb.loads(row[7], hex=True)
    data.append({
        "iris_code":        row[0],
        "nom_iris":         row[1],
        "commune":          row[2],
        "nb_clients":       row[3],
        "taux_penetration": float(row[4]) if row[4] else 0,
        "panier_moyen":     float(row[5]) if row[5] else 0,
        "freq_moyenne":     float(row[6]) if row[6] else 0,
        "geometry":         geom
    })

gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")
print(f"\n📊 Top 10 IRIS par taux de pénétration :")
print(f"{'IRIS':<12} {'Quartier':<30} {'Commune':<20} {'Clients':>7} {'Taux':>6}")
print("-" * 80)
top10 = gdf.nlargest(10, "nb_clients")
for _, row in top10.iterrows():
    print(f"{row.iris_code:<12} {str(row.nom_iris)[:29]:<30} {str(row.commune)[:19]:<20} {row.nb_clients:>7} {row.taux_penetration:>6.1f}‰")

# ── Sauvegarde GeoJSON ───────────────────────
gdf.to_file("data/exports/penetration_iris.geojson", driver="GeoJSON")
print("\n💾 GeoJSON sauvegardé !")

# ── Carte choroplèthe Folium ─────────────────
print("\n🗺️  Génération carte choroplèthe...")

carte = folium.Map(
    location=[50.6292, 3.0573],
    zoom_start=11,
    tiles="CartoDB positron"
)

# Choroplèthe
folium.Choropleth(
    geo_data=gdf.__geo_interface__,
    data=gdf,
    columns=["iris_code", "nb_clients"],
    key_on="feature.properties.iris_code",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.3,
    legend_name="Nombre de clients par IRIS",
    nan_fill_color="lightgrey",
).add_to(carte)

# Tooltips
folium.GeoJson(
    gdf.__geo_interface__,
    style_function=lambda x: {
        "fillOpacity": 0,
        "weight": 0
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["nom_iris", "commune", "nb_clients", "panier_moyen"],
        aliases=["Quartier", "Commune", "Clients", "Panier moyen"],
        localize=True
    )
).add_to(carte)

# Magasin
folium.Marker(
    location=[50.6292, 3.0573],
    popup="🏪 Decathlon Lille Nord",
    icon=folium.Icon(color="red", icon="shopping-cart", prefix="fa")
).add_to(carte)

carte.save("data/exports/carte_penetration.html")
print("✅ Carte choroplèthe sauvegardée !")
print("👉 Ouvre : data/exports/carte_penetration.html")

cur.close()
conn.close()
print("\n🎉 Analyse terminée !")