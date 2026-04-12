import os
from dotenv import load_dotenv

# Charge les variables du fichier .env
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / ".env")

# ── Base de données ──────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST"),
    "port":     os.getenv("DB_PORT"),
    "dbname":   os.getenv("DB_NAME"),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# URL de connexion pour SQLAlchemy
DB_URL = (
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
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
NB_CLIENTS    = 2000   # nombre de clients à générer
RAYON_MAX_KM  = 30     # rayon maximum autour du magasin
NB_SEGMENTS   = 5      # nombre de segments clients attendus
SRID          = 4326   # système de coordonnées (WGS84)