import streamlit as st
from streamlit_gsheets import GSheetsConnection
url = "https://docs.google.com/spreadsheets/d/1JDy9md2VZPz4JbYtRPJLs81_3jUK47nx6GYQjgU8qNY/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)
data = conn.read(spreadsheet=url, usecols=[0, 1])
st.dataframe(data)

#https://github.com/streamlit/gsheets-connection
#https://st-gsheets.streamlit.app/Service_Account_Example