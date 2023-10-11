import streamlit as st
from streamlit_extras.switch_page_button import switch_page

def do_stuff_on_page_load():
    st.set_page_config(layout="wide")

do_stuff_on_page_load()

st.title('PI DA - Juan E Flórez')
st.markdown('***')

st.markdown('## This Web App will show the Dashboard of the project')

if st.button("Go to Dashboard"):
    switch_page("Dashboard")

