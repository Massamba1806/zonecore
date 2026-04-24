# 🗺️ ZoneCore — Analyse spatiale des zones de chalandise

> **Prouve que les zones de chalandise en cercle sont fausses.**  
> Zone réelle découverte : **727 km²** vs 314 km² (cercle classique) → **+132% de territoire**

[![Streamlit App](https://img.shields.io/badge/Dashboard-Live-brightgreen?style=for-the-badge&logo=streamlit)](https://zonecore.streamlit.app)
[![GitHub](https://img.shields.io/badge/GitHub-Code-blue?style=for-the-badge&logo=github)](https://github.com/Massamba1806/zonecore)

---

## 🎯 Problématique

Les géomarketeurs tracent des **cercles** autour des magasins pour délimiter leurs zones de chalandise. C'est rapide — mais inexact. Les clients ne se déplacent pas en cercle. Ils suivent les routes, les transports, leurs habitudes.

**ZoneCore** reconstruit la vraie zone à partir des comportements réels de 2 000 clients.

---

## 📊 Résultats clés

| Métrique | Cercle classique | ZoneCore |
|---|---|---|
| Surface zone | 314 km² | **727 km²** |
| Territoire découvert | — | **+132%** |
| Segments clients | 1 (uniforme) | **5 clusters distincts** |
| Isochrones | 0 | **12 multimodales** |

### Les 5 segments DBSCAN découverts
| Cluster | Profil | Panier moyen | Fréquence |
|---|---|---|---|
| 1 | Famille périurbaine | 119€ | 2x/mois |
| 2 | Étudiant vélo | 36€ | 4x/mois |
| 3 | Urbain proche | — | 14.8x/an |
| 4 | CSP+ voiture | 87€ | 1x/mois |
| 5 | Senior transport | 52€ | 2x/mois |

---

## 🏗️ Architecture technique