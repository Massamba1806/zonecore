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
        mode_transport,
        panier_moyen,
        frequence_achat,
        (ST_Distance(
            ST_Transform(geometry, 2154),
            ST_Transform(ST_SetSRID(ST_MakePoint(3.0573, 50.6292), 4326), 2154)
        ) / 1000.0)::numeric as distance_km
    FROM raw_data.clients
    WHERE geometry IS NOT NULL
    AND ST_Distance(
        ST_Transform(geometry, 2154),
        ST_Transform(ST_SetSRID(ST_MakePoint(3.0573, 50.6292), 4326), 2154)
    ) < 35000;
"""
df = pd.read_sql(query, conn)
conn.close()

COULEURS = {
    "voiture":   "#E74C3C",
    "velo":      "#2ECC71",
    "transport": "#F39C12",
    "marche":    "#9B59B6",
}

fig, ax = plt.subplots(figsize=(7, 5), facecolor="none")
ax.set_facecolor("none")

for mode, group in df.groupby("mode_transport"):
    couleur = COULEURS.get(mode, "#AAAAAA")
    taille  = (group["frequence_achat"] * 4) + 20
    ax.scatter(
        group["distance_km"],
        group["panier_moyen"],
        s=taille,
        c=couleur,
        alpha=0.55,
        edgecolors="white",
        linewidths=0.4,
        label=mode.capitalize(),
        zorder=3,
    )

z = np.polyfit(df["distance_km"], df["panier_moyen"], 1)
p = np.poly1d(z)
x_line = np.linspace(float(df["distance_km"].min()), float(df["distance_km"].max()), 200)
ax.plot(x_line, p(x_line), color="#333333", linewidth=1.4,
        linestyle="--", alpha=0.6, zorder=2)

ax.set_xlabel("Distance au magasin (km)", fontsize=10, color="#333333", labelpad=8)
ax.set_ylabel("Panier moyen (€)", fontsize=10, color="#333333", labelpad=8)
ax.tick_params(colors="#555555", labelsize=8)
ax.spines[["top","right"]].set_visible(False)
ax.spines[["left","bottom"]].set_color("#CCCCCC")
ax.grid(axis="y", color="#EEEEEE", linewidth=0.7, zorder=0)
ax.set_xlim(-0.5, 30)

patches = [
    mpatches.Patch(color=c, label=m.capitalize())
    for m, c in COULEURS.items()
]
ax.legend(handles=patches, fontsize=8, framealpha=0,
          labelcolor="#333333", loc="upper left")

plt.tight_layout()
plt.savefig(
    "data/exports/scatter_distance_panier.png",
    dpi=300,
    transparent=True,
    bbox_inches="tight"
)
print("✅ PNG exporté : data/exports/scatter_distance_panier.png")