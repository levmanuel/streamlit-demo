import streamlit as st
st.text("hello")
test = st.secrets["gcp_service_account"]["type"]
st.text("hello")
st.text(test)