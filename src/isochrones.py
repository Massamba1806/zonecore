import requests
import geopandas as gpd
import folium
import time
import os
from pathlib import Path
from dotenv import load_dotenv
from shapely.geometry import shape

# ── Config ───────────────────────────────────
load_dotenv(Path("C:/Users/Admin/Desktop/zonecore/.env"))
ORS_API_KEY = os.getenv("ORS_API_KEY")

STORE_LAT = 50.6292
STORE_LON = 3.0573

print("🔑 Clé API chargée ✅")
print("🗺️  Génération des isochrones...")

# ── Paramètres par cluster ───────────────────
CONFIGS = [
    {"cluster": 0, "profile": "driving-car",     "ranges": [600, 1200, 1800], "nom": "Famille voiture",   "couleur": "#E74C3C"},
    {"cluster": 1, "profile": "driving-car",     "ranges": [900, 1800],       "nom": "Suburban voiture",  "couleur": "#3498DB"},
    {"cluster": 2, "profile": "cycling-regular", "ranges": [600, 1200],       "nom": "Etudiant vélo",     "couleur": "#2ECC71"},
    {"cluster": 3, "profile": "driving-car",     "ranges": [900, 1800],       "nom": "Urbain transport",  "couleur": "#F39C12"},
    {"cluster": 4, "profile": "foot-walking",    "ranges": [300, 600, 900],   "nom": "Urbain marche",     "couleur": "#9B59B6"},
]

# ── Appel API ORS ────────────────────────────
def get_isochrone(profile, ranges):
    url = f"https://api.openrouteservice.org/v2/isochrones/{profile}"
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type":  "application/json"
    }
    body = {
        "locations":  [[STORE_LON, STORE_LAT]],
        "range":      ranges,
        "range_type": "time",
    }
    r = requests.post(url, headers=headers, json=body, timeout=30)
    print(f"   Status API : {r.status_code}")
    if r.status_code == 200:
        return r.json()
    else:
        print(f"   Erreur : {r.text[:200]}")
        return None

# ── Génère et collecte ───────────────────────
all_features = []

for config in CONFIGS:
    print(f"\n▸ Cluster {config['cluster']} — {config['nom']}")
    data = get_isochrone(config["profile"], config["ranges"])

    if data and "features" in data:
        for feat in data["features"]:
            duree = feat["properties"].get("value", 0) // 60
            geom  = shape(feat["geometry"])
            all_features.append({
                "cluster":  config["cluster"],
                "nom":      config["nom"],
                "couleur":  config["couleur"],
                "duree":    duree,
                "geometry": geom
            })
            print(f"   ✅ Isochrone {duree} min OK")
    time.sleep(2)

print(f"\n📊 Total isochrones : {len(all_features)}")

# ── GeoDataFrame + export ────────────────────
gdf = gpd.GeoDataFrame(all_features, crs="EPSG:4326")
gdf.to_file("data/exports/isochrones.geojson", driver="GeoJSON")
print("💾 GeoJSON sauvegardé !")

# ── Carte Folium ─────────────────────────────
carte = folium.Map(
    location=[STORE_LAT, STORE_LON],
    zoom_start=11,
    tiles="CartoDB positron"
)

folium.Marker(
    location=[STORE_LAT, STORE_LON],
    popup="🏪 Decathlon Lille Nord",
    icon=folium.Icon(color="red", icon="shopping-cart", prefix="fa")
).add_to(carte)

for config in CONFIGS:
    groupe = folium.FeatureGroup(name=config["nom"])
    subset = gdf[gdf["cluster"] == config["cluster"]].sort_values(
        "duree", ascending=False
    )
    for _, row in subset.iterrows():
        folium.GeoJson(
            row.geometry.__geo_interface__,
            style_function=lambda x, c=config["couleur"]: {
                "fillColor":   c,
                "color":       c,
                "weight":      2,
                "fillOpacity": 0.15,
            },
            tooltip=f"{config['nom']} — {row.duree} min"
        ).add_to(groupe)
    groupe.add_to(carte)

folium.LayerControl(collapsed=False).add_to(carte)
carte.save("data/exports/carte_isochrones.html")
print("✅ Carte sauvegardée : data/exports/carte_isochrones.html")
print("👉 Ouvre ce fichier dans ton navigateur !")
print("\n🎉 Terminé !")