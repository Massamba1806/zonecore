import geopandas as gpd
import psycopg2
import pandas as pd
from sqlalchemy import create_engine, text

# ── Connexion directe psycopg2 ───────────────
print("🔌 Connexion à PostGIS...")
conn = psycopg2.connect(
    host="127.0.0.1",
    port=5432,
    dbname="zonecore",
    user="postgres",
    password="Khodia1571@"
)
print("✅ Connexion psycopg2 OK !")

# ── Connexion SQLAlchemy ─────────────────────
engine = create_engine(
    "postgresql+psycopg2://",
    creator=lambda: psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        dbname="zonecore",
        user="postgres",
        password="Khodia1571@"
    )
)
print("✅ Connexion SQLAlchemy OK !")

# ── Charge le GeoJSON ────────────────────────
print("\n📂 Chargement des clients...")
gdf = gpd.read_file("data/exports/clients_bruts.geojson")
print(f"✅ {len(gdf)} clients chargés")

# ── Prépare les colonnes ─────────────────────
gdf = gdf.rename(columns={"segment_theorique": "segment"})

colonnes = [
    "client_id", "adresse", "commune", "code_postal",
    "longitude", "latitude", "frequence_achat",
    "panier_moyen", "mode_transport", "segment", "geometry"
]
gdf = gdf[colonnes]

# ── Import dans PostGIS ──────────────────────
print("\n📤 Import dans PostGIS...")
gdf.to_postgis(
    name="clients",
    con=engine,
    schema="raw_data",
    if_exists="replace",
    index=False,
)
print(f"✅ {len(gdf)} clients importés dans raw_data.clients !")

# ── Vérification ─────────────────────────────
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM raw_data.clients;")
nb = cur.fetchone()[0]
print(f"✅ Vérification : {nb} lignes dans PostGIS")

cur.execute("""
    SELECT segment, COUNT(*) as nb
    FROM raw_data.clients
    GROUP BY segment
    ORDER BY segment;
""")
print(f"\n📊 Répartition par segment :")
for row in cur.fetchall():
    print(f"   Segment {row[0]} : {row[1]} clients")

cur.close()
conn.close()