import streamlit as st
from streamlit_gsheets import GSheetsConnection
import plotly.graph_objects as go
import pandas as pd

conn = st.connection("gsheets", type=GSheetsConnection)

if "df" not in st.session_state:
    try:
        st.session_state.df = conn.read(worksheet="Feuille 1", ttl=600)
    except Exception as e:
        st.error(f"Impossible de charger la Google Sheet : {e}")
        st.stop()

if st.button("🔄 Mettre à jour les données"):
    try:
        st.session_state.df = conn.read(worksheet="Feuille 1", ttl=0)
        st.success("Données mises à jour ✅")
    except Exception as e:
        st.error(f"Erreur lors de la mise à jour : {e}")

df = st.session_state.df.copy()
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date", "Close"]).sort_values("Date")

# --- En-tête ---
st.title("📈 Tesla (TSLA) — Cours sur 90 jours")
st.caption('Source : `GOOGLEFINANCE("TSLA";"price";TODAY()-90;TODAY())`')

# --- Métriques ---
price_last = df["Close"].iloc[-1]
price_first = df["Close"].iloc[0]
price_min = df["Close"].min()
price_max = df["Close"].max()
variation = price_last - price_first
variation_pct = variation / price_first * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Prix actuel", f"${price_last:.2f}", f"{variation:+.2f} $ ({variation_pct:+.1f}%)")
col2.metric("Prix il y a 90 j", f"${price_first:.2f}")
col3.metric("Plus bas", f"${price_min:.2f}")
col4.metric("Plus haut", f"${price_max:.2f}")

# --- Graphique Plotly ---
color = "#00c853" if variation >= 0 else "#d50000"
fill_color = "rgba(0,200,83,0.1)" if variation >= 0 else "rgba(213,0,0,0.1)"

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df["Date"],
    y=df["Close"],
    mode="lines",
    name="Cours",
    line=dict(color=color, width=2),
    fill="tozeroy",
    fillcolor=fill_color,
    hovertemplate="<b>%{x|%d %b %Y}</b><br>$%{y:.2f}<extra></extra>",
))
fig.update_layout(
    xaxis_title=None,
    yaxis_title="Prix (USD)",
    hovermode="x unified",
    showlegend=False,
    margin=dict(l=0, r=0, t=10, b=0),
    yaxis=dict(tickprefix="$", gridcolor="#f0f0f0"),
    xaxis=dict(gridcolor="#f0f0f0"),
    plot_bgcolor="white",
    paper_bgcolor="white",
)
st.plotly_chart(fig, use_container_width=True)

# --- Tableau ---
with st.expander("Voir les données brutes"):
    st.dataframe(
        df.sort_values("Date", ascending=False).reset_index(drop=True),
        use_container_width=True,
        column_config={
            "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
            "Close": st.column_config.NumberColumn("Prix ($)", format="$%.2f"),
        },
    )
