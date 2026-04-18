import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

conn = psycopg2.connect(
    host="127.0.0.1", port=5432,
    dbname="zonecore", user="postgres",
    password="Khodia1571@"
)

query = """
    SELECT
        cluster_dbscan,
        COUNT(*)                                    as nb_clients,
        ROUND(AVG(panier_moyen)::numeric, 0)        as panier_moyen,
        ROUND(AVG(frequence_achat)::numeric, 1)     as frequence,
        ROUND(SUM(panier_moyen * frequence_achat)::numeric / 
              SUM(COUNT(*)) OVER()::numeric, 0)     as contribution_ca,
        mode() WITHIN GROUP (ORDER BY mode_transport) as transport
    FROM raw_data.clients
    WHERE cluster_dbscan != -1
    GROUP BY cluster_dbscan
    ORDER BY cluster_dbscan;
"""
df = pd.read_sql(query, conn)
conn.close()

NOMS = {
    0: "Famille\npériurbaine",
    1: "Suburban\nvoiture",
    2: "Étudiant\nvélo",
    3: "Urbain\ntransport",
    4: "Urbain\nproche"
}
COULEURS = {
    0: "#E74C3C",
    1: "#3498DB",
    2: "#2ECC71",
    3: "#F39C12",
    4: "#9B59B6"
}

df["nom"] = df["cluster_dbscan"].map(NOMS)
df["couleur"] = df["cluster_dbscan"].map(COULEURS)

print(df[["nom", "nb_clients", "panier_moyen", "frequence", "transport"]])

# ── Graphique radar/barres multiples ─────────
fig, axes = plt.subplots(1, 3, figsize=(10, 4), facecolor="none")
for ax in axes:
    ax.set_facecolor("none")

# Graphique 1 — Nombre de clients
axes[0].barh(df["nom"], df["nb_clients"],
             color=df["couleur"], alpha=0.85)
axes[0].set_xlabel("Nombre de clients", fontsize=9, color="#444")
axes[0].spines[["top","right","left"]].set_visible(False)
axes[0].spines["bottom"].set_color("#CCCCCC")
axes[0].tick_params(colors="#555", labelsize=8)
for i, v in enumerate(df["nb_clients"]):
    axes[0].text(v + 10, i, str(v), va="center",
                 fontsize=8, color="#444")

# Graphique 2 — Panier moyen
axes[1].barh(df["nom"], df["panier_moyen"],
             color=df["couleur"], alpha=0.85)
axes[1].set_xlabel("Panier moyen (€)", fontsize=9, color="#444")
axes[1].spines[["top","right","left"]].set_visible(False)
axes[1].spines["bottom"].set_color("#CCCCCC")
axes[1].tick_params(colors="#555", labelsize=8)
axes[1].set_yticklabels([])
for i, v in enumerate(df["panier_moyen"]):
    axes[1].text(v + 1, i, f"{v}€", va="center",
                 fontsize=8, color="#444")

# Graphique 3 — Fréquence
axes[2].barh(df["nom"], df["frequence"],
             color=df["couleur"], alpha=0.85)
axes[2].set_xlabel("Fréquence (visites/an)", fontsize=9, color="#444")
axes[2].spines[["top","right","left"]].set_visible(False)
axes[2].spines["bottom"].set_color("#CCCCCC")
axes[2].tick_params(colors="#555", labelsize=8)
axes[2].set_yticklabels([])
for i, v in enumerate(df["frequence"]):
    axes[2].text(v + 0.1, i, f"{v}x", va="center",
                 fontsize=8, color="#444")

plt.tight_layout()
plt.savefig(
    "data/exports/graphique_profils_clusters.png",
    dpi=300,
    transparent=True,
    bbox_inches="tight"
)
print("\n✅ PNG exporté : data/exports/graphique_profils_clusters.png")