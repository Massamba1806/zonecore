import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

fig, ax = plt.subplots(figsize=(6, 3.5), facecolor="none")
ax.set_facecolor("none")

categories = ["Surface\ncaptée (km²)", "Clients\ncaptés (%)"]
valeurs_cercle = [314, 38]
valeurs_reelle = [727, 87]

x = np.arange(len(categories))
width = 0.35

bars1 = ax.bar(x - width/2, valeurs_cercle, width,
               color="#E74C3C", alpha=0.85,
               label="Cercle classique 10km")

bars2 = ax.bar(x + width/2, valeurs_reelle, width,
               color="#1A3557", alpha=0.85,
               label="Zone réelle DBSCAN")

# Valeurs sur les barres
for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 8,
            f"{int(bar.get_height())}",
            ha="center", va="bottom",
            fontsize=9, color="#E74C3C", fontweight="bold")

for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 8,
            f"{int(bar.get_height())}",
            ha="center", va="bottom",
            fontsize=9, color="#1A3557", fontweight="bold")

ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=10, color="#444444")
ax.tick_params(axis="y", colors="#888888", labelsize=8)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.spines["bottom"].set_color("#CCCCCC")
ax.yaxis.set_visible(False)
ax.grid(False)

patches = [
    mpatches.Patch(color="#E74C3C", label="Cercle classique 10km"),
    mpatches.Patch(color="#1A3557", label="Zone réelle DBSCAN"),
]
ax.legend(handles=patches, fontsize=8, framealpha=0,
          labelcolor="#444444", loc="upper left")

plt.tight_layout()
plt.savefig(
    "data/exports/graphique_comparaison.png",
    dpi=300,
    transparent=True,
    bbox_inches="tight"
)
print("✅ PNG exporté : data/exports/graphique_comparaison.png")