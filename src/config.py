import os
from pathlib import Path
from dotenv import load_dotenv

# Charge les variables du fichier .env
load_dotenv(Path(__file__).parent.parent / ".env")

# ── Base de données ──────────────────────────
DB_CONFIG = {
    "host":     "127.0.0.1",
    "port":     "5432",
    "dbname":   os.getenv("DB_NAME"),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# URL de connexion pour SQLAlchemy
DB_URL = (
    f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@127.0.0.1:5432/{DB_CONFIG['dbname']}"
)

# ── APIs ─────────────────────────────────────
ORS_API_KEY = os.getenv("ORS_API_KEY")

# ── Magasin de référence ─────────────────────
STORE = {
    "name": os.getenv("STORE_NAME"),
    "lat":  float(os.getenv("STORE_LAT")),
    "lon":  float(os.getenv("STORE_LON")),
    "city": os.getenv("STORE_CITY"),
}

# ── Paramètres du projet ─────────────────────
NB_CLIENTS    = 2000
RAYON_MAX_KM  = 30
NB_SEGMENTS   = 5
SRID          = 4326