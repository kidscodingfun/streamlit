import pandas as pd
import streamlit as st
data  = pd.read_csv("DataSet/student_marks.csv")
st.set_page_config(layout="wide")
st.table(data)
st.write(data.dtypes)
st.write(data.shape)
st.table(data.describe())
