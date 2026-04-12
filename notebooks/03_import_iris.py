import geopandas as gpd
import psycopg2
from sqlalchemy import create_engine
from tqdm import tqdm

# ── Connexion ────────────────────────────────
print("🔌 Connexion à PostGIS...")
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
print("✅ Connexion OK !")

# ── Codes INSEE de la métropole lilloise ─────
CODES_INSEE_LILLE = [
    "59350",  # Lille
    "59512",  # Roubaix
    "59599",  # Tourcoing
    "59009",  # Lambersart
    "59152",  # Croix
    "59220",  # Faches-Thumesnil
    "59246",  # Hellemmes
    "59320",  # Loos
    "59378",  # Marcq-en-Barœul
    "59386",  # Mons-en-Barœul
    "59391",  # Mouvaux
    "59410",  # Hem
    "59553",  # Villeneuve-d'Ascq
    "59009",  # Lambersart
    "59560",  # Wasquehal
    "59640",  # Wattrelos
    "59339",  # Lomme
]

# ── Charge le shapefile IRIS France ─────────
print("\n📂 Chargement du shapefile IRIS France...")
print("   (fichier lourd ~128Mo, patience...)")
gdf_france = gpd.read_file("data/raw/iris/CONTOURS-IRIS.shp")
print(f"✅ {len(gdf_france)} IRIS France chargés")
print(f"   Colonnes : {list(gdf_france.columns)}")

# ── Filtre sur la métropole lilloise ─────────
print("\n🔍 Filtrage sur la métropole lilloise...")
gdf_lille = gdf_france[
    gdf_france["INSEE_COM"].isin(CODES_INSEE_LILLE)
].copy()
print(f"✅ {len(gdf_lille)} IRIS retenus pour la métropole")

# ── Reprojection en WGS84 ────────────────────
print("\n🔄 Reprojection WGS84 (EPSG:4326)...")
gdf_lille = gdf_lille.to_crs(epsg=4326)
print("✅ Reprojection OK")

# ── Renomme les colonnes ─────────────────────
gdf_lille = gdf_lille.rename(columns={
    "CODE_IRIS": "iris_code",
    "NOM_IRIS":  "nom_iris",
    "INSEE_COM": "code_insee",
    "NOM_COM":   "commune",
})

# Garde les colonnes utiles
colonnes = ["iris_code", "nom_iris", "code_insee", "commune", "geometry"]
colonnes_presentes = [c for c in colonnes if c in gdf_lille.columns]
gdf_lille = gdf_lille[colonnes_presentes]

print(f"\n📊 Aperçu des données :")
print(gdf_lille[["iris_code", "nom_iris", "commune"]].head(10))

# ── Sauvegarde GeoJSON local ─────────────────
gdf_lille.to_file("data/exports/iris_lille.geojson", driver="GeoJSON")
print(f"\n💾 GeoJSON sauvegardé : data/exports/iris_lille.geojson")

# ── Import dans PostGIS ──────────────────────
print("\n📤 Import dans PostGIS...")
gdf_lille.to_postgis(
    name="iris",
    con=engine,
    schema="raw_data",
    if_exists="replace",
    index=False,
)
print(f"✅ {len(gdf_lille)} IRIS importés dans raw_data.iris !")

# ── Vérification ─────────────────────────────
conn = psycopg2.connect(
    host="127.0.0.1", port=5432,
    dbname="zonecore", user="postgres",
    password="Khodia1571@"
)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM raw_data.iris;")
print(f"✅ Vérification PostGIS : {cur.fetchone()[0]} IRIS")
cur.execute("""
    SELECT commune, COUNT(*) as nb_iris
    FROM raw_data.iris
    GROUP BY commune
    ORDER BY nb_iris DESC
    LIMIT 10;
""")
print(f"\n📊 IRIS par commune :")
for row in cur.fetchall():
    print(f"   {row[0]} : {row[1]} IRIS")

cur.close()
conn.close()