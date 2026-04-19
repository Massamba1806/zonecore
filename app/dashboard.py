import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium

# ── Configuration page ───────────────────────
st.set_page_config(
    page_title="ZoneCore — Massamba DIENG",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS Custom ───────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A3557 0%, #0D2137 100%);
    }
    [data-testid="stSidebar"] * { color: white !important; }
    .main { background-color: #F8F9FA; }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        margin: 0;
        line-height: 1.1;
    }
    .metric-label {
        font-size: 12px;
        color: #888;
        margin: 4px 0 0 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-sub {
        font-size: 11px;
        color: #aaa;
        margin: 2px 0 0 0;
    }
    .section-title {
        font-size: 13px;
        font-weight: 600;
        color: #1A3557;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 24px 0 12px 0;
        padding-bottom: 6px;
        border-bottom: 2px solid #E8EEF4;
    }
    .cluster-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-top: 4px solid;
        height: 100%;
    }
    .block-container { padding-top: 0rem; }

    /* PAGE D'ACCUEIL */
    .splash-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        background: linear-gradient(135deg, #0D2137 0%, #1A3557 50%, #2E6DA4 100%);
        margin: -1rem -1rem 0 -1rem;
        padding: 40px;
        text-align: center;
    }
    .splash-logo {
        font-size: 72px;
        margin-bottom: 20px;
    }
    .splash-name {
        font-size: 52px;
        font-weight: 800;
        color: white;
        letter-spacing: 3px;
        margin: 0;
        text-transform: uppercase;
    }
    .splash-title {
        font-size: 20px;
        color: #B8D4F0;
        margin: 12px 0 8px 0;
        font-weight: 300;
        letter-spacing: 4px;
        text-transform: uppercase;
    }
    .splash-divider {
        width: 80px;
        height: 3px;
        background: #E74C3C;
        margin: 20px auto;
        border-radius: 2px;
    }
    .splash-project {
        font-size: 16px;
        color: #7FB3D3;
        margin: 0 0 40px 0;
        font-style: italic;
    }
    .splash-btn {
        background: #E74C3C;
        color: white !important;
        padding: 16px 48px;
        border-radius: 50px;
        font-size: 16px;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        border: none;
        cursor: pointer;
        box-shadow: 0 8px 24px rgba(231,76,60,0.4);
    }
    .splash-stats {
        display: flex;
        gap: 48px;
        margin-top: 48px;
        justify-content: center;
    }
    .splash-stat {
        text-align: center;
    }
    .splash-stat-num {
        font-size: 32px;
        font-weight: 700;
        color: white;
    }
    .splash-stat-label {
        font-size: 11px;
        color: #7FB3D3;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# ── Constantes ───────────────────────────────
COULEURS = {
    0: "#E74C3C",
    1: "#3498DB",
    2: "#2ECC71",
    3: "#F39C12",
    4: "#9B59B6"
}
NOMS = {
    0: "Famille périurbaine",
    1: "Suburban voiture",
    2: "Étudiant vélo",
    3: "Urbain transport",
    4: "Urbain proche"
}
TRANSPORT_ICONS = {
    "voiture":   "🚗",
    "velo":      "🚲",
    "transport": "🚌",
    "marche":    "🚶"
}

# ── Chargement données ───────────────────────
@st.cache_data
def load_data():
    gdf = gpd.read_file("data/exports/clients_bruts.geojson")
    gdf = gdf[gdf["segment_theorique"].notna()].copy()
    gdf = gdf.rename(columns={"segment_theorique": "cluster_dbscan"})
    gdf["cluster_dbscan"] = gdf["cluster_dbscan"].astype(int)
    gdf["commune"] = gdf.get("commune", "Inconnue")
    if "commune" not in gdf.columns:
        gdf["commune"] = "Inconnue"
    gdf["commune"] = gdf["commune"].fillna("Inconnue")
    return pd.DataFrame(gdf.drop(columns="geometry"))

df = load_data()
df["nom_cluster"] = df["cluster_dbscan"].map(NOMS)
df["couleur"]     = df["cluster_dbscan"].map(COULEURS)

# ── SESSION STATE ────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "splash"

# ════════════════════════════════════════════
# PAGE SPLASH
# ════════════════════════════════════════════
if st.session_state.page == "splash":

    st.markdown("""
        <div class="splash-container">
            <div class="splash-logo">🗺️</div>
            <p class="splash-name">Massamba Dieng</p>
            <p class="splash-title">Chargé d'études Géomarketing</p>
            <div class="splash-divider"></div>
            <p class="splash-project">ZoneCore — Analyse spatiale des zones de chalandise<br>
            Decathlon Lille Nord · Métropole Lilloise · 2026</p>
            <div class="splash-stats">
                <div class="splash-stat">
                    <div class="splash-stat-num">2 000</div>
                    <div class="splash-stat-label">Clients analysés</div>
                </div>
                <div class="splash-stat">
                    <div class="splash-stat-num">5</div>
                    <div class="splash-stat-label">Clusters DBSCAN</div>
                </div>
                <div class="splash-stat">
                    <div class="splash-stat-num">281</div>
                    <div class="splash-stat-label">IRIS métropole</div>
                </div>
                <div class="splash-stat">
                    <div class="splash-stat-num">4</div>
                    <div class="splash-stat-label">Cartes produites</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🚀  Explorer le dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

# ════════════════════════════════════════════
# PAGE DASHBOARD
# ════════════════════════════════════════════
else:

    # ── SIDEBAR ──────────────────────────────
    with st.sidebar:
        st.markdown("""
            <div style='text-align:center; padding:20px 0 24px 0;'>
                <div style='font-size:32px;'>🗺️</div>
                <div style='font-size:18px; font-weight:700; color:white;'>ZoneCore</div>
                <div style='font-size:10px; color:#B8D4F0; margin-top:4px;
                            text-transform:uppercase; letter-spacing:1px;'>
                    Massamba Dieng
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        st.markdown("<p style='font-size:11px; color:#B8D4F0; text-transform:uppercase; letter-spacing:1px;'>Segments clients</p>", unsafe_allow_html=True)
        clusters_selec = st.multiselect(
            "Segments",
            options=list(NOMS.values()),
            default=list(NOMS.values()),
            label_visibility="collapsed"
        )

        st.markdown("<p style='font-size:11px; color:#B8D4F0; text-transform:uppercase; letter-spacing:1px; margin-top:16px;'>Mode de transport</p>", unsafe_allow_html=True)
        transports_selec = st.multiselect(
            "Transport",
            options=["voiture", "velo", "transport", "marche"],
            default=["voiture", "velo", "transport", "marche"],
            label_visibility="collapsed"
        )

        st.markdown("<p style='font-size:11px; color:#B8D4F0; text-transform:uppercase; letter-spacing:1px; margin-top:16px;'>Panier moyen (€)</p>", unsafe_allow_html=True)
        panier_range = st.slider(
            "Panier",
            min_value=0, max_value=250,
            value=(0, 250),
            label_visibility="collapsed"
        )

        st.markdown("---")

        if st.button("⬅️ Accueil", use_container_width=True):
            st.session_state.page = "splash"
            st.rerun()

        st.markdown("""
            <div style='font-size:10px; color:#B8D4F0; text-align:center; padding-top:12px;'>
                Python · PostGIS · QGIS · Streamlit<br>
                <span style='color:#7FB3D3;'>Métropole Lilloise · 2026</span>
            </div>
        """, unsafe_allow_html=True)

    # ── Filtre ────────────────────────────────
    df_f = df[
        (df["nom_cluster"].isin(clusters_selec)) &
        (df["mode_transport"].isin(transports_selec)) &
        (df["panier_moyen"] >= panier_range[0]) &
        (df["panier_moyen"] <= panier_range[1])
    ]

    # ── HEADER ────────────────────────────────
    st.markdown(f"""
        <div style='background:linear-gradient(135deg,#1A3557,#2E6DA4);
                    padding:24px 32px; border-radius:16px; margin-bottom:20px;'>
            <p style='font-size:26px; font-weight:700; color:white; margin:0;'>
                🗺️ ZoneCore — Zones de chalandise
            </p>
            <p style='font-size:13px; color:#B8D4F0; margin:6px 0 0 0;'>
                Decathlon Lille Nord · DBSCAN · 
                <b style='color:white;'>{len(df_f):,}</b> clients affichés
            </p>
        </div>
    """, unsafe_allow_html=True)

    # ── MÉTRIQUES ─────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        (c1, f"{len(df_f):,}",
         "Clients", "filtrés", "#E74C3C"),
        (c2, f"{df_f['panier_moyen'].mean():.0f} €" if len(df_f) else "—",
         "Panier moyen", "tous segments", "#3498DB"),
        (c3, f"{df_f['frequence_achat'].mean():.1f}x" if len(df_f) else "—",
         "Fréquence", "visites / an", "#2ECC71"),
        (c4, str(df_f['cluster_dbscan'].nunique()),
         "Clusters", "actifs", "#F39C12"),
        (c5, str(df_f['commune'].nunique()) if 'commune' in df_f.columns else "—",
         "Communes", "représentées", "#9B59B6"),
    ]
    for col, val, label, sub, color in metrics:
        with col:
            st.markdown(f"""
                <div class="metric-card" style="border-left-color:{color};">
                    <p class="metric-value" style="color:{color};">{val}</p>
                    <p class="metric-label">{label}</p>
                    <p class="metric-sub">{sub}</p>
                </div>
            """, unsafe_allow_html=True)

    # ── CARTE + GRAPHIQUES ─────────────────────
    map_col, chart_col = st.columns([3, 2])

    with map_col:
        st.markdown('<p class="section-title">🗺️ Carte interactive</p>',
                    unsafe_allow_html=True)
        carte = folium.Map(
            location=[50.6292, 3.0573],
            zoom_start=11,
            tiles="CartoDB positron"
        )
        folium.Marker(
            location=[50.6292, 3.0573],
            popup="🏪 Decathlon Lille Nord",
            icon=folium.Icon(color="red", icon="star", prefix="fa")
        ).add_to(carte)

        for cid in df_f["cluster_dbscan"].unique():
            subset = df_f[df_f["cluster_dbscan"] == cid]
            couleur = COULEURS[cid]
            groupe  = folium.FeatureGroup(name=NOMS[cid])
            cluster_marker = MarkerCluster().add_to(groupe)
            for _, row in subset.iterrows():
                folium.CircleMarker(
                    location=[row.latitude, row.longitude],
                    radius=4,
                    color=couleur,
                    fill=True,
                    fill_color=couleur,
                    fill_opacity=0.7,
                    popup=folium.Popup(
                        f"<b>{row.client_id}</b><br>"
                        f"Cluster : {NOMS[cid]}<br>"
                        f"Panier : {row.panier_moyen:.0f}€<br>"
                        f"Transport : {TRANSPORT_ICONS.get(row.mode_transport,'')} "
                        f"{row.mode_transport}<br>"
                        f"Fréquence : {row.frequence_achat}x/an",
                        max_width=200
                    )
                ).add_to(cluster_marker)
            groupe.add_to(carte)

        folium.LayerControl(collapsed=False).add_to(carte)
        st_folium(carte, width="stretch", height=450)

    with chart_col:
        st.markdown('<p class="section-title">📊 Analyse par segment</p>',
                    unsafe_allow_html=True)

        if len(df_f) > 0:
            stats = df_f.groupby("nom_cluster").agg(
                panier=("panier_moyen", "mean"),
                frequence=("frequence_achat", "mean"),
                nb=("client_id", "count")
            ).reset_index()

            fig1 = px.bar(
                stats.sort_values("panier"),
                x="panier", y="nom_cluster",
                orientation="h",
                color="nom_cluster",
                color_discrete_map={v: COULEURS[k] for k, v in NOMS.items()},
                text=stats.sort_values("panier")["panier"].apply(
                    lambda x: f"{x:.0f}€"),
                labels={"panier": "Panier moyen (€)", "nom_cluster": ""},
            )
            fig1.update_layout(
                showlegend=False,
                plot_bgcolor="white",
                paper_bgcolor="white",
                margin=dict(l=0, r=20, t=10, b=30),
                height=200,
                font=dict(size=11),
                xaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
                yaxis=dict(showgrid=False),
            )
            fig1.update_traces(textposition="outside")
            st.plotly_chart(fig1, width="stretch")

            fig2 = px.bar(
                stats.sort_values("frequence"),
                x="frequence", y="nom_cluster",
                orientation="h",
                color="nom_cluster",
                color_discrete_map={v: COULEURS[k] for k, v in NOMS.items()},
                text=stats.sort_values("frequence")["frequence"].apply(
                    lambda x: f"{x:.1f}x"),
                labels={"frequence": "Fréquence (visites/an)", "nom_cluster": ""},
            )
            fig2.update_layout(
                showlegend=False,
                plot_bgcolor="white",
                paper_bgcolor="white",
                margin=dict(l=0, r=20, t=10, b=30),
                height=200,
                font=dict(size=11),
                xaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
                yaxis=dict(showgrid=False),
            )
            fig2.update_traces(textposition="outside")
            st.plotly_chart(fig2, width="stretch")

    # ── FICHES CLUSTERS ────────────────────────
    st.markdown('<p class="section-title">🎯 Fiches détail par segment</p>',
                unsafe_allow_html=True)

    cols = st.columns(5)
    for i, (cid, nom) in enumerate(NOMS.items()):
        subset  = df_f[df_f["cluster_dbscan"] == cid]
        couleur = COULEURS[cid]
        if len(subset) == 0:
            continue
        transport_dom = subset["mode_transport"].mode()[0]
        icon = TRANSPORT_ICONS.get(transport_dom, "")
        with cols[i]:
            st.markdown(f"""
                <div class="cluster-card" style="border-top-color:{couleur};">
                    <div style="font-size:11px; font-weight:700; color:{couleur};
                                text-transform:uppercase; letter-spacing:1px;">
                        Cluster {cid}
                    </div>
                    <div style="font-size:14px; font-weight:600; color:#1A3557;
                                margin:6px 0; line-height:1.3;">{nom}</div>
                    <hr style="border:none; border-top:1px solid #F0F0F0; margin:10px 0;">
                    <div style="display:flex; justify-content:space-between; margin:6px 0;">
                        <span style="font-size:11px; color:#888;">Clients</span>
                        <span style="font-size:13px; font-weight:600;
                                     color:#1A3557;">{len(subset):,}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin:6px 0;">
                        <span style="font-size:11px; color:#888;">Panier</span>
                        <span style="font-size:13px; font-weight:600;
                                     color:{couleur};">
                            {subset['panier_moyen'].mean():.0f} €</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin:6px 0;">
                        <span style="font-size:11px; color:#888;">Fréquence</span>
                        <span style="font-size:13px; font-weight:600;
                                     color:#1A3557;">
                            {subset['frequence_achat'].mean():.1f}x/an</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin:6px 0;">
                        <span style="font-size:11px; color:#888;">Transport</span>
                        <span style="font-size:13px;">{icon} {transport_dom}</span>
                    </div>
                    <div style="margin-top:10px; background:{couleur}22;
                                border-radius:6px; padding:6px 8px; text-align:center;">
                        <span style="font-size:10px; color:{couleur}; font-weight:600;">
                            CA estimé : 
                            {subset['panier_moyen'].mean() * subset['frequence_achat'].mean():.0f}
                            €/client/an
                        </span>
                    </div>
                </div>
            """, unsafe_allow_html=True)