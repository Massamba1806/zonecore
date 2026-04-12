import psycopg2
import pandas as pd
import geopandas as gpd
import numpy as np
import folium
from folium.plugins import MarkerCluster
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from shapely.geometry import Point, MultiPoint
from shapely.ops import unary_union
import warnings
warnings.filterwarnings("ignore")

# ── Connexion ────────────────────────────────
print("🔌 Connexion à PostGIS...")
conn = psycopg2.connect(
    host="127.0.0.1", port=5432,
    dbname="zonecore", user="postgres",
    password="Khodia1571@"
)
print("✅ Connexion OK !")

# ── Charge les clients depuis PostGIS ────────
print("\n📂 Chargement des clients...")
query = """
    SELECT
        client_id, longitude, latitude,
        frequence_achat, panier_moyen,
        mode_transport, segment,
        iris_code
    FROM raw_data.clients
    WHERE longitude IS NOT NULL
    AND latitude IS NOT NULL;
"""
df = pd.read_sql(query, conn)
print(f"✅ {len(df)} clients chargés")

# ── Prépare les features pour DBSCAN ─────────
print("\n🔧 Préparation des features...")

# Encode le mode de transport en numérique
transport_map = {
    "marche": 0, "velo": 1,
    "transport": 2, "voiture": 3
}
df["transport_num"] = df["mode_transport"].map(transport_map).fillna(2)

# Features géographiques + comportementales
features = df[[
    "longitude",
    "latitude",
    "frequence_achat",
    "panier_moyen",
    "transport_num"
]].copy()

# Normalisation
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)
print("✅ Features normalisées")

# ── DBSCAN géographique ──────────────────────
print("\n🤖 Lancement du DBSCAN...")
dbscan = DBSCAN(
    eps=0.3,          # rayon du voisinage
    min_samples=15,   # minimum de points pour former un cluster
    metric="euclidean"
)
labels = dbscan.fit_predict(features_scaled)

df["cluster_dbscan"] = labels
n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
n_bruit    = list(labels).count(-1)

print(f"✅ DBSCAN terminé !")
print(f"   Clusters découverts : {n_clusters}")
print(f"   Points bruit        : {n_bruit}")

# ── Analyse des clusters ─────────────────────
print(f"\n📊 Profil de chaque cluster :")
print("-" * 75)

cluster_ids = sorted([c for c in df["cluster_dbscan"].unique() if c != -1])

for cluster_id in cluster_ids:
    subset = df[df["cluster_dbscan"] == cluster_id]
    
    transport_dominant = subset["mode_transport"].mode()[0]
    panier_moy         = subset["panier_moyen"].mean()
    freq_moy           = subset["frequence_achat"].mean()
    nb_clients         = len(subset)
    
    print(f"\n  Cluster {cluster_id} ({nb_clients} clients)")
    print(f"  ├── Panier moyen   : {panier_moy:.0f}€")
    print(f"  ├── Fréquence moy  : {freq_moy:.1f} visites/an")
    print(f"  └── Transport dom  : {transport_dominant}")

print(f"\n  Bruit / outliers  : {n_bruit} clients")

# ── Sauvegarde dans PostGIS ──────────────────
print(f"\n📤 Sauvegarde des clusters dans PostGIS...")
cur = conn.cursor()
cur.execute("""
    ALTER TABLE raw_data.clients
    ADD COLUMN IF NOT EXISTS cluster_dbscan INTEGER;
""")
conn.commit()

for _, row in df.iterrows():
    cur.execute("""
        UPDATE raw_data.clients
        SET cluster_dbscan = %s
        WHERE client_id = %s;
    """, (int(row["cluster_dbscan"]), row["client_id"]))

conn.commit()
print(f"✅ Clusters sauvegardés dans PostGIS !")

# ── Carte des clusters ───────────────────────
print(f"\n🗺️  Génération de la carte des clusters...")

COULEURS_CLUSTER = [
    "#E74C3C", "#3498DB", "#2ECC71",
    "#F39C12", "#9B59B6", "#1ABC9C",
    "#E67E22", "#34495E"
]

gdf = gpd.GeoDataFrame(
    df,
    geometry=[Point(row.longitude, row.latitude) for row in df.itertuples()],
    crs="EPSG:4326"
)

carte = folium.Map(
    location=[50.6292, 3.0573],
    zoom_start=11,
    tiles="CartoDB positron"
)

# Magasin
folium.Marker(
    location=[50.6292, 3.0573],
    popup="🏪 Decathlon Lille Nord",
    icon=folium.Icon(color="red", icon="shopping-cart", prefix="fa")
).add_to(carte)

# Clients par cluster
for cluster_id in sorted(df["cluster_dbscan"].unique()):
    if cluster_id == -1:
        couleur = "#AAAAAA"
        nom     = "Bruit / outliers"
    else:
        couleur = COULEURS_CLUSTER[cluster_id % len(COULEURS_CLUSTER)]
        subset  = df[df["cluster_dbscan"] == cluster_id]
        panier  = subset["panier_moyen"].mean()
        freq    = subset["frequence_achat"].mean()
        nom     = f"Cluster {cluster_id} — {panier:.0f}€ — {freq:.1f}x/an"

    groupe  = folium.FeatureGroup(name=nom)
    clients = gdf[gdf["cluster_dbscan"] == cluster_id]

    for _, row in clients.iterrows():
        folium.CircleMarker(
            location=[row.latitude, row.longitude],
            radius=4,
            color=couleur,
            fill=True,
            fill_color=couleur,
            fill_opacity=0.7,
            popup=folium.Popup(
                f"<b>{row.client_id}</b><br>"
                f"Cluster : {row.cluster_dbscan}<br>"
                f"Panier : {row.panier_moyen}€<br>"
                f"Transport : {row.mode_transport}",
                max_width=200
            )
        ).add_to(groupe)

    groupe.add_to(carte)

folium.LayerControl(collapsed=False).add_to(carte)

output = "data/exports/carte_clusters_dbscan.html"
carte.save(output)
print(f"✅ Carte sauvegardée : {output}")
print("👉 Ouvre ce fichier dans ton navigateur !")

cur.close()
conn.close()
print("\n🎉 DBSCAN terminé avec succès !")