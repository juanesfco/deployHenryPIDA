import streamlit as st

def do_stuff_on_page_load():
    st.set_page_config(layout="wide")

do_stuff_on_page_load()

if st.checkbox('show text'):
    st.write('hola')

with st.sidebar:
    st.write("Select a range on the slider (it represents movie score) \
       to view the total number of movies in a genre that falls \
       within that range ")
    #create a slider to hold user scores
    new_score_rating = st.slider(label = "Choose a value:",
                                    min_value = 1.0,
                                    max_value = 10.0,
                                    value = (3.0,4.0))

    #create a multiselect widget to display genre
    new_genre_list = st.multiselect('Choose Genre:',
                                            genre_list, default = ['Animation',\
                                            'Horror',  'Fantasy', 'Romance'])
    #create a selectbox option that holds all unique years
    year = st.selectbox('Choose a Year',
        year_list, 0)