import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta

st.set_page_config(page_title="Open-Meteo API", layout="wide")
st.title("🌤️ Open-Meteo API Explorer")
st.write("Exploration d'une API météo publique et gratuite — aucune clé requise.")
st.caption("Documentation : https://open-meteo.com/en/docs")

BASE_URL = "https://api.open-meteo.com/v1"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

CITIES = {
    "Paris": (48.8566, 2.3522),
    "London": (51.5074, -0.1278),
    "New York": (40.7128, -74.0060),
    "Tokyo": (35.6762, 139.6503),
    "Sydney": (-33.8688, 151.2093),
    "Dubaï": (25.2048, 55.2708),
    "São Paulo": (-23.5505, -46.6333),
}

# --- Sidebar ---
st.sidebar.header("Paramètres")
city = st.sidebar.selectbox("Ville", list(CITIES.keys()))
lat, lon = CITIES[city]
st.sidebar.caption(f"Lat: {lat} / Lon: {lon}")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📡 Météo actuelle", "📈 Prévisions 7 jours", "🕰️ Historique 30 jours"])


# ── Tab 1 : Météo actuelle ──────────────────────────────────────────────────
with tab1:
    st.subheader(f"Conditions actuelles — {city}")
    st.code(f"GET {BASE_URL}/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m,relative_humidity_2m,precipitation,weathercode", language="bash")

    if st.button("Appeler l'API", key="btn_current"):
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,wind_speed_10m,relative_humidity_2m,precipitation,weathercode",
            "timezone": "auto",
        }
        try:
            r = requests.get(f"{BASE_URL}/forecast", params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
            current = data.get("current", {})
            units = data.get("current_units", {})

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🌡️ Température", f"{current.get('temperature_2m')} {units.get('temperature_2m')}")
            col2.metric("💨 Vent", f"{current.get('wind_speed_10m')} {units.get('wind_speed_10m')}")
            col3.metric("💧 Humidité", f"{current.get('relative_humidity_2m')} {units.get('relative_humidity_2m')}")
            col4.metric("🌧️ Précipitations", f"{current.get('precipitation')} {units.get('precipitation')}")

            with st.expander("Réponse JSON brute"):
                st.json(data)
        except requests.exceptions.Timeout:
            st.error("L'API n'a pas répondu dans les 10 secondes.")
        except Exception as e:
            st.error(f"Erreur : {e}")


# ── Tab 2 : Prévisions 7 jours ─────────────────────────────────────────────
with tab2:
    st.subheader(f"Prévisions sur 7 jours — {city}")
    st.code(f"GET {BASE_URL}/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max", language="bash")

    if st.button("Appeler l'API", key="btn_forecast"):
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
            "timezone": "auto",
            "forecast_days": 7,
        }
        try:
            r = requests.get(f"{BASE_URL}/forecast", params=params, timeout=10)
            r.raise_for_status()
            daily = r.json().get("daily", {})
            df = pd.DataFrame(daily)
            df["time"] = pd.to_datetime(df["time"])

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["time"], y=df["temperature_2m_max"],
                name="T° max", line=dict(color="#e74c3c", width=2),
                fill=None,
            ))
            fig.add_trace(go.Scatter(
                x=df["time"], y=df["temperature_2m_min"],
                name="T° min", line=dict(color="#3498db", width=2),
                fill="tonexty", fillcolor="rgba(52,152,219,0.1)",
            ))
            fig.update_layout(
                yaxis_title="Température (°C)",
                xaxis_title=None,
                hovermode="x unified",
                plot_bgcolor="white",
                yaxis=dict(gridcolor="#f0f0f0"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(t=30, b=0),
            )
            st.plotly_chart(fig, use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                st.bar_chart(df.set_index("time")["precipitation_sum"], color="#3498db")
                st.caption("Précipitations (mm/jour)")
            with col2:
                st.bar_chart(df.set_index("time")["windspeed_10m_max"], color="#95a5a6")
                st.caption("Vent max (km/h)")

            with st.expander("Données brutes"):
                st.dataframe(df, use_container_width=True, hide_index=True)
        except requests.exceptions.Timeout:
            st.error("L'API n'a pas répondu dans les 10 secondes.")
        except Exception as e:
            st.error(f"Erreur : {e}")


# ── Tab 3 : Historique 30 jours ────────────────────────────────────────────
with tab3:
    st.subheader(f"Données historiques — {city}")
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=29)
    st.code(f"GET {ARCHIVE_URL}?latitude={lat}&longitude={lon}&start_date={start}&end_date={end}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum", language="bash")

    if st.button("Appeler l'API", key="btn_historical"):
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": str(start),
            "end_date": str(end),
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto",
        }
        try:
            r = requests.get(ARCHIVE_URL, params=params, timeout=10)
            r.raise_for_status()
            daily = r.json().get("daily", {})
            df = pd.DataFrame(daily)
            df["time"] = pd.to_datetime(df["time"])

            t_mean = ((df["temperature_2m_max"] + df["temperature_2m_min"]) / 2)
            col1, col2, col3 = st.columns(3)
            col1.metric("T° moyenne", f"{t_mean.mean():.1f} °C")
            col2.metric("T° max sur la période", f"{df['temperature_2m_max'].max():.1f} °C")
            col3.metric("Précipitations totales", f"{df['precipitation_sum'].sum():.1f} mm")

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["time"], y=df["temperature_2m_max"],
                name="T° max", line=dict(color="#e74c3c", width=1.5),
            ))
            fig.add_trace(go.Scatter(
                x=df["time"], y=df["temperature_2m_min"],
                name="T° min", line=dict(color="#3498db", width=1.5),
                fill="tonexty", fillcolor="rgba(52,152,219,0.08)",
            ))
            fig.add_trace(go.Scatter(
                x=df["time"], y=t_mean,
                name="T° moyenne", line=dict(color="#f39c12", width=2, dash="dot"),
            ))
            fig.update_layout(
                yaxis_title="Température (°C)",
                hovermode="x unified",
                plot_bgcolor="white",
                yaxis=dict(gridcolor="#f0f0f0"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(t=30, b=0),
            )
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("Données brutes"):
                st.dataframe(df, use_container_width=True, hide_index=True)
        except requests.exceptions.Timeout:
            st.error("L'API n'a pas répondu dans les 10 secondes.")
        except Exception as e:
            st.error(f"Erreur : {e}")
