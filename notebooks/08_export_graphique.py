import pandas as pd
import psycopg2

# ── Connexion ────────────────────────────────
conn = psycopg2.connect(
    host="127.0.0.1", port=5432,
    dbname="zonecore", user="postgres",
    password="Khodia1571@"
)

# ── Récupère les données clusters ────────────
query = """
    SELECT
        cluster_dbscan,
        COUNT(*)                                    as nb_clients,
        ROUND(AVG(panier_moyen)::numeric, 0)        as panier_moyen,
        ROUND(AVG(frequence_achat)::numeric, 1)     as frequence,
        mode() WITHIN GROUP (ORDER BY mode_transport) as transport
    FROM raw_data.clients
    WHERE cluster_dbscan != -1
    GROUP BY cluster_dbscan
    ORDER BY cluster_dbscan;
"""
df = pd.read_sql(query, conn)
conn.close()

# ── Noms des clusters ────────────────────────
noms = {
    0: "Famille périurbaine",
    1: "Suburban voiture",
    2: "Étudiant vélo",
    3: "Urbain transport",
    4: "Urbain proche"
}
couleurs = {
    0: "#E74C3C",
    1: "#3498DB",
    2: "#2ECC71",
    3: "#F39C12",
    4: "#9B59B6"
}

df["nom_cluster"]  = df["cluster_dbscan"].map(noms)
df["couleur"]      = df["cluster_dbscan"].map(couleurs)

print(df[["nom_cluster", "nb_clients", "panier_moyen", "frequence", "transport"]])

# ── Export Excel ─────────────────────────────
output = "data/exports/clusters_graphique.xlsx"

with pd.ExcelWriter(output, engine="openpyxl") as writer:
    # Onglet données
    df_export = df[[
        "nom_cluster", "nb_clients",
        "panier_moyen", "frequence", "transport"
    ]].rename(columns={
        "nom_cluster":  "Segment",
        "nb_clients":   "Nombre de clients",
        "panier_moyen": "Panier moyen (€)",
        "frequence":    "Fréquence (visites/an)",
        "transport":    "Transport dominant"
    })
    df_export.to_excel(writer, sheet_name="Clusters", index=False)

print(f"\n✅ Excel exporté : {output}")
print("👉 Ouvre ce fichier et crée le graphique en barres horizontales")