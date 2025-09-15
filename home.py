import streamlit as st

st.set_page_config(
    page_title="Home",
)

st.write("# Welcome")

pg = st.navigation([st.Page("pages/students.py"), st.Page("pages/nba.py")])
pg.run()
