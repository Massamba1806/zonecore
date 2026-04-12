import geopandas as gpd
import folium
from folium.plugins import MarkerCluster

# ── Couleurs par segment ─────────────────────
COULEURS = {
    1: "#E74C3C",   # Rouge    — Urbain proche
    2: "#3498DB",   # Bleu     — Suburban voiture
    3: "#2ECC71",   # Vert     — Famille périurbaine
    4: "#F39C12",   # Orange   — Etudiant
    5: "#9B59B6",   # Violet   — CSP+ lointain
}

NOMS_SEGMENTS = {
    1: "Urbain proche",
    2: "Suburban voiture",
    3: "Famille périurbaine",
    4: "Etudiant",
    5: "CSP+ lointain",
}

# ── Charge les données ───────────────────────
print("📂 Chargement des données...")
gdf = gpd.read_file("data/exports/clients_bruts.geojson")
print(f"✅ {len(gdf)} clients chargés")

# ── Crée la carte centrée sur Lille ─────────
carte = folium.Map(
    location=[50.6292, 3.0573],
    zoom_start=11,
    tiles="CartoDB positron"
)

# ── Ajoute le magasin Decathlon ──────────────
folium.Marker(
    location=[50.6292, 3.0573],
    popup="🏪 Decathlon Lille Nord",
    tooltip="Decathlon Lille Nord",
    icon=folium.Icon(color="red", icon="shopping-cart", prefix="fa")
).add_to(carte)

# ── Ajoute les clients par segment ──────────
for segment in sorted(gdf["segment_theorique"].unique()):
    groupe = folium.FeatureGroup(
        name=f"Segment {segment} — {NOMS_SEGMENTS[segment]}"
    )
    clients_seg = gdf[gdf["segment_theorique"] == segment]
    cluster = MarkerCluster().add_to(groupe)

    for _, row in clients_seg.iterrows():
        folium.CircleMarker(
            location=[row.latitude, row.longitude],
            radius=5,
            color=COULEURS[segment],
            fill=True,
            fill_color=COULEURS[segment],
            fill_opacity=0.7,
            popup=folium.Popup(
                f"""
                <b>Client :</b> {row.client_id}<br>
                <b>Adresse :</b> {row.adresse}<br>
                <b>Commune :</b> {row.commune}<br>
                <b>Transport :</b> {row.mode_transport}<br>
                <b>Fréquence :</b> {row.frequence_achat} visites/an<br>
                <b>Panier moyen :</b> {row.panier_moyen}€<br>
                <b>Segment :</b> {NOMS_SEGMENTS[segment]}
                """,
                max_width=250
            )
        ).add_to(cluster)

    groupe.add_to(carte)

# ── Contrôle des couches ─────────────────────
folium.LayerControl(collapsed=False).add_to(carte)

# ── Sauvegarde ───────────────────────────────
output = "data/exports/carte_clients.html"
carte.save(output)
print(f"\n🗺️  Carte sauvegardée : {output}")
print("👉 Ouvre ce fichier dans ton navigateur pour voir la carte !")