import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="LCR Simulation Demo", page_icon="📈")

st.title("LCR Simulation Tool")
st.write(
    "Selon cette norme, l'encours d'actifs liquides de haute qualité doit au moins être égal "
    "aux sorties nettes de trésorerie pendant les 30 jours qui suivent la date d'arrêté du calcul du ratio."
)

st.latex(r"LCR = \frac{HQLA}{Outflows - \min(0{,}75 \times Outflows,\ Inflows)}")

# --- Valeurs de base ---
st.subheader("Valeurs de base")
col1, col2, col3 = st.columns(3)
with col1:
    hqla_base = st.number_input("HQLA", min_value=0.0, value=20.0, step=1.0)
with col2:
    outflow_base = st.number_input("Outflows", min_value=0.1, value=45.0, step=1.0)
with col3:
    inflow_base = st.number_input("Inflows", min_value=0.0, value=25.0, step=1.0)

# --- Facteurs de stress ---
st.subheader("Facteurs de stress (%)")
col1, col2, col3 = st.columns(3)
with col1:
    factor_hqla = st.slider("HQLA Factor %", -100, 100, 0)
with col2:
    factor_out = st.slider("Outflows Factor %", -100, 100, 0)
with col3:
    factor_in = st.slider("Inflows Factor %", -100, 100, 0)

# --- Calcul des valeurs stressées ---
hqla = hqla_base * (1 + factor_hqla / 100)
outflow = outflow_base * (1 + factor_out / 100)
inflow = inflow_base * (1 + factor_in / 100)

inflow_cap = 0.75 * outflow
inflow_capped = min(inflow_cap, inflow)
net_outflow_base = outflow_base - min(0.75 * outflow_base, inflow_base)
net_outflow = outflow - inflow_capped

lcr_base = round(100 * hqla_base / net_outflow_base, 2) if net_outflow_base > 0 else float("inf")
lcr = round(100 * hqla / net_outflow, 2) if net_outflow > 0 else float("inf")

# --- Tableaux de détail ---
col1, col2 = st.columns(2)

with col1:
    st.write("**Détail LCR**")
    df_lcr = pd.DataFrame({
        "": ["HQLA", "Outflows", "Inflows", "LCR (%)"],
        "Base": [hqla_base, outflow_base, inflow_base, lcr_base],
        "Stressé": [round(hqla, 2), round(outflow, 2), round(inflow, 2), lcr],
        "Delta": [
            round(hqla - hqla_base, 2),
            round(outflow - outflow_base, 2),
            round(inflow - inflow_base, 2),
            round(lcr - lcr_base, 2),
        ],
    })
    st.dataframe(df_lcr, hide_index=True)

with col2:
    st.write("**Détail Net Outflow**")
    df_nof = pd.DataFrame({
        "": ["Outflows", "75% Outflows", "Inflows", "Min(75% OF, IF)", "Net Outflow"],
        "Base": [
            outflow_base,
            round(0.75 * outflow_base, 2),
            inflow_base,
            round(min(0.75 * outflow_base, inflow_base), 2),
            round(net_outflow_base, 2),
        ],
        "Stressé": [
            round(outflow, 2),
            round(0.75 * outflow, 2),
            round(inflow, 2),
            round(inflow_capped, 2),
            round(net_outflow, 2),
        ],
    })
    st.dataframe(df_nof, hide_index=True)

if inflow_cap < inflow:
    st.warning("⚠️ Cas Inflows cappés : les entrées dépassent 75 % des sorties.")
else:
    st.info("Cas normal : Inflows non cappés.")

lcr_color = "green" if lcr >= 100 else "red"
st.markdown(
    f"**LCR stressé : <span style='color:{lcr_color}'>{lcr}%</span>** "
    f"(seuil réglementaire Bâle III : 100 %)",
    unsafe_allow_html=True,
)

# --- Simulation 30 jours ---
st.subheader("Simulation : hausse quotidienne des Outflows sur 30 jours")
of_factor = st.slider("Taux de hausse journalier des Outflows (%)", 0, 100, 1)

days, lcr_sim, outflow_sim = [], [], []
current_outflow = outflow  # part de l'état stressé

for i in range(30):
    current_outflow = round((1 + of_factor / 100) * current_outflow, 2)
    current_inflow_capped = min(0.75 * current_outflow, inflow)
    current_net = current_outflow - current_inflow_capped
    current_lcr = round(100 * hqla / current_net, 1) if current_net > 0 else float("inf")
    days.append(i + 1)
    outflow_sim.append(current_outflow)
    lcr_sim.append(current_lcr)

fig = go.Figure()
fig.add_trace(go.Bar(x=days, y=lcr_sim, name="LCR (%)", marker_color=[
    "#28a745" if v >= 100 else "#dc3545" for v in lcr_sim
]))
fig.add_hline(
    y=100,
    line_dash="dash",
    line_color="black",
    annotation_text="Seuil Bâle III (100 %)",
    annotation_position="top right",
)
fig.update_layout(
    xaxis_title="Jour",
    yaxis_title="LCR (%)",
    showlegend=False,
)
st.plotly_chart(fig, use_container_width=True)

breach_day = next((d for d, v in zip(days, lcr_sim) if v < 100), None)
if breach_day:
    st.error(f"Le LCR passe sous 100 % au jour {breach_day}.")
else:
    st.success("Le LCR reste au-dessus de 100 % sur les 30 jours.")
