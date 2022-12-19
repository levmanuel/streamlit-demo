import folium
import streamlit as st
import pandas as pd

from streamlit_folium import st_folium

st.set_page_config(page_title="Holidays in Norway", page_icon="✈️")

st.title("Holidays in Norway ✈️")
st.write("Day-to-Day Planner")

# center on Oslo
m = folium.Map(location=[59.91512811000568, 10.739105977295354], zoom_start=8)
folium.Marker([59.91512811000568, 10.739105977295354], popup="Oslo", tooltip="Oslo").add_to(m)
  
# Create a list of coordinates representing the points along the route
coordinates = [[59.91512811000568, 10.739105977295354], [60.46905260044231, 5.371412422001533]]

# Add the itinerary to the map as a PolyLine
folium.PolyLine(coordinates, color="red", weight=2.5, opacity=1).add_to(m)

# call to render Folium map in Streamlit
# st_data = st_folium(m, width=725)

#Dataframe
nof = pd.DataFrame({
"Name": ["Outflow", "75cpt_Outflow", "Inflow", "Min(0.75 OF, IF)", "Net_Ouflow"],
"start": [45, 0.75*45, 25, min(0.75*45, 25), 20],
"updated": [45, 0.75*45, 25, min(0.75*45, 25), 20]})

col1, col2 = st.columns(2)
with col1:
    st.dataframe(nof)

with col2:
    st_data = st_folium(m, width=725)
