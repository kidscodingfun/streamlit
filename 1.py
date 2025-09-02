import pandas as pd
import streamlit as st
data  = pd.read_csv("marksheet.csv")
st.set_page_config(layout="wide")
st.table(data.head())
