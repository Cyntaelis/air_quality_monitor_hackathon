import streamlit as st
import pandas as pd
import numpy as np
from spatial import gazetteer
from airnow_connection import AirnowConnection

st.set_page_config(
    page_title="Weather",
    page_icon="tornado",
    layout="wide",
)

st.title("Current Air Quality Monitor Readings")
st.subheader("Only works on US ZIP codes with a monitoring station within 20mi. Data from airnow.gov")
conn = st.experimental_connection("airnow", type=AirnowConnection)

columns = [
    "Site Name",
    "Latitude",
    "Longitude",
    "PM2.5",
    "PM10",
    "OZONE",
    "Station Distance",
    "Station Direction"]

df = pd.DataFrame(np.zeros((0,len(columns))), columns=columns, index=[])

with st.form(key="my_form"):
    _ = st.text_input(
    "Zip code",
    "",
    key="zip_code")
    st.form_submit_button("Lookup")

if st.session_state.zip_code != "":
    results = conn.query(st.session_state.zip_code)
    if results is None:
        st.text("Error: invalid zip code or server issues")
    else:
        df = results

st.dataframe(df, use_container_width=True, hide_index=True)


