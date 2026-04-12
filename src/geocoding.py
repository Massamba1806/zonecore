import requests
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
from tqdm import tqdm
from src.config import STORE, NB_CLIENTS, SRID

# ── Reproductibilité ─────────────────────────
np.random.seed(42)

# ── Communes de la métropole lilloise ────────
COMMUNES = [
    "Lille", "Roubaix", "Tourcoing", "Villeneuve-d-Ascq",
    "Marcq-en-Baroeul", "Lambersart", "Hellemmes", "Lomme",
    "Loos", "Faches-Thumesnil", "Mons-en-Baroeul", "Wasquehal",
    "Mouvaux", "Croix", "Wattrelos", "Hem"
]

# ── Profils clients réalistes ────────────────
PROFILS = {
    1: {
        "nom":         "Urbain proche",
        "poids":       0.25,
        "transport":   ["marche", "velo", "transport"],
        "transport_p": [0.40, 0.35, 0.25],
        "frequence":   (8, 24),
        "panier":      (25, 55),
    },
    2: {
        "nom":         "Suburban voiture",
        "poids":       0.30,
        "transport":   ["voiture", "transport"],
        "transport_p": [0.85, 0.15],
        "frequence":   (4, 12),
        "panier":      (65, 110),
    },
    3: {
        "nom":         "Famille périurbaine",
        "poids":       0.20,
        "transport":   ["voiture"],
        "transport_p": [1.0],
        "frequence":   (2, 6),
        "panier":      (95, 160),
    },
    4: {
        "nom":         "Etudiant",
        "poids":       0.15,
        "transport":   ["velo", "transport", "marche"],
        "transport_p": [0.45, 0.40, 0.15],
        "frequence":   (6, 18),
        "panier":      (20, 45),
    },
    5: {
        "nom":         "CSP+ lointain",
        "poids":       0.10,
        "transport":   ["voiture"],
        "transport_p": [1.0],
        "frequence":   (1, 4),
        "panier":      (130, 220),
    },
}


def get_adresses_ban(commune: str, nb: int) -> list:
    """
    Appelle l'API Base Adresse Nationale pour récupérer
    de vraies adresses dans une commune.
    """
    url = "https://api-adresse.data.gouv.fr/search/"
    params = {
        "q":     f"rue {commune}",
        "limit": min(nb, 50),
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        features = data.get("features", [])

        adresses = []
        for f in features:
            props  = f.get("properties", {})
            coords = f.get("geometry", {}).get("coordinates", [])

            if len(coords) < 2:
                continue

            adresses.append({
                "adresse":     props.get("label", f"Rue de {commune}"),
                "commune":     props.get("city", commune),
                "code_postal": props.get("postcode", ""),
                "longitude":   float(coords[0]),
                "latitude":    float(coords[1]),
            })

        return adresses

    except requests.exceptions.Timeout:
        print(f"\n    ⏱️  Timeout pour {commune}, on continue...")
        return []
    except Exception as e:
        print(f"\n    ⚠️  Erreur BAN pour {commune} : {e}")
        return []


def generer_clients() -> gpd.GeoDataFrame:
    """
    Génère NB_CLIENTS clients fictifs réalistes
    basés sur de vraies adresses lilloises.
    """
    print(f"\n🏗️  Génération de {NB_CLIENTS} clients...")
    tous_clients = []
    client_id = 1

    for segment, profil in PROFILS.items():
        nb_segment = int(NB_CLIENTS * profil["poids"])
        print(f"\n  ▸ Segment {segment} — {profil['nom']} ({nb_segment} clients)")

        # Collecte les adresses depuis l'API BAN
        adresses_pool = []
        for commune in tqdm(COMMUNES, desc="    API BAN"):
            nb_par_commune = max(10, nb_segment // len(COMMUNES) + 5)
            adresses = get_adresses_ban(commune, nb_par_commune)
            adresses_pool.extend(adresses)

        if not adresses_pool:
            print(f"    ❌ Aucune adresse récupérée pour ce segment.")
            continue

        print(f"    ✅ {len(adresses_pool)} adresses récupérées")

        # Génère les clients
        for i in range(nb_segment):
            adr = adresses_pool[i % len(adresses_pool)]

            transport = np.random.choice(
                profil["transport"],
                p=profil["transport_p"]
            )
            frequence = int(np.random.randint(
                profil["frequence"][0],
                profil["frequence"][1]
            ))
            panier = round(float(np.random.uniform(
                profil["panier"][0],
                profil["panier"][1]
            )), 2)

            tous_clients.append({
                "client_id":         f"CLI{client_id:05d}",
                "adresse":           adr["adresse"],
                "commune":           adr["commune"],
                "code_postal":       adr["code_postal"],
                "longitude":         adr["longitude"],
                "latitude":          adr["latitude"],
                "frequence_achat":   frequence,
                "panier_moyen":      panier,
                "mode_transport":    transport,
                "segment_theorique": segment,
            })
            client_id += 1

    # Convertit en GeoDataFrame
    df = pd.DataFrame(tous_clients)

    if df.empty:
        print("\n❌ Aucun client généré. Vérifie ta connexion internet.")
        return gpd.GeoDataFrame()

    geometry = [Point(row.longitude, row.latitude) for row in df.itertuples()]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=f"EPSG:{SRID}")

    print(f"\n✅ {len(gdf)} clients générés avec succès !")
    print(f"\n📊 Répartition par segment :")
    print(gdf["segment_theorique"].value_counts().sort_index())
    print(f"\n📊 Panier moyen par segment :")
    print(gdf.groupby("segment_theorique")["panier_moyen"].mean().round(2))

    return gdf


if __name__ == "__main__":
    gdf = generer_clients()

    if not gdf.empty:
        output_path = "data/exports/clients_bruts.geojson"
        gdf.to_file(output_path, driver="GeoJSON")
        print(f"\n💾 Fichier sauvegardé : {output_path}")