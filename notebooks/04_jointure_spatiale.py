import psycopg2

# ── Connexion ────────────────────────────────
print("🔌 Connexion à PostGIS...")
conn = psycopg2.connect(
    host="127.0.0.1",
    port=5432,
    dbname="zonecore",
    user="postgres",
    password="Khodia1571@"
)
cur = conn.cursor()
print("✅ Connexion OK !")

# ── Ajoute la colonne iris_code si manquante ─
print("\n🔧 Vérification de la colonne iris_code...")
cur.execute("""
    ALTER TABLE raw_data.clients
    ADD COLUMN IF NOT EXISTS iris_code VARCHAR(9);
""")
conn.commit()
print("✅ Colonne iris_code OK !")

# ── Jointure spatiale dans PostGIS ───────────
print("\n🔗 Jointure spatiale clients ↔ IRIS...")
cur.execute("""
    UPDATE raw_data.clients c
    SET iris_code = i.iris_code
    FROM raw_data.iris i
    WHERE ST_Within(c.geometry, i.geometry);
""")
conn.commit()
print("✅ Jointure spatiale terminée !")

# ── Vérifie les résultats ────────────────────
cur.execute("""
    SELECT
        COUNT(*)                        as total_clients,
        COUNT(iris_code)                as clients_avec_iris,
        COUNT(*) - COUNT(iris_code)     as clients_sans_iris
    FROM raw_data.clients;
""")
row = cur.fetchone()
print(f"\n📊 Résultats de la jointure :")
print(f"   Total clients  : {row[0]}")
print(f"   Avec IRIS      : {row[1]}")
print(f"   Sans IRIS      : {row[2]}")

# ── Top 10 IRIS les plus peuplés ─────────────
cur.execute("""
    SELECT
        c.iris_code,
        i.nom_iris,
        i.commune,
        COUNT(*)                                    as nb_clients,
        ROUND(AVG(c.panier_moyen)::numeric, 2)      as panier_moyen
    FROM raw_data.clients c
    JOIN raw_data.iris i ON c.iris_code = i.iris_code
    GROUP BY c.iris_code, i.nom_iris, i.commune
    ORDER BY nb_clients DESC
    LIMIT 10;
""")
rows = cur.fetchall()
print(f"\n📊 Top 10 IRIS avec le plus de clients :")
print(f"{'IRIS':<15} {'Quartier':<35} {'Commune':<25} {'Clients':>7} {'Panier':>8}")
print("-" * 95)
for row in rows:
    iris    = str(row[0])
    quartier = str(row[1])[:34]
    commune  = str(row[2])[:24]
    clients  = row[3]
    panier   = row[4]
    print(f"{iris:<15} {quartier:<35} {commune:<25} {clients:>7} {panier:>8}€")

# ── Répartition par commune ──────────────────
cur.execute("""
    SELECT
        i.commune,
        COUNT(*)                                    as nb_clients,
        ROUND(AVG(c.panier_moyen)::numeric, 2)      as panier_moyen,
        ROUND(AVG(c.frequence_achat)::numeric, 1)   as freq_moyenne
    FROM raw_data.clients c
    JOIN raw_data.iris i ON c.iris_code = i.iris_code
    GROUP BY i.commune
    ORDER BY nb_clients DESC;
""")
rows = cur.fetchall()
print(f"\n📊 Clients par commune :")
print(f"{'Commune':<25} {'Clients':>8} {'Panier':>8} {'Fréquence':>10}")
print("-" * 55)
for row in rows:
    print(f"{str(row[0]):<25} {row[1]:>8} {row[2]:>8}€ {row[3]:>10}/an")

cur.close()
conn.close()
print("\n✅ Analyse terminée !")