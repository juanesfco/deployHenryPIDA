import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

def do_stuff_on_page_load():
    st.set_page_config(layout="wide")

do_stuff_on_page_load()

st.markdown(f'''
<style>
.appview-container .main .block-container{{
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;    }}
</style>
''', unsafe_allow_html=True,
)

with st.sidebar:
    year = st.selectbox('Choose a Year',['All Time',2016,2017,2018,2019,2020,2021], 0)

df_hom = pd.read_csv('data/df_homicides.csv',parse_dates=['datetime'])
try:
    totHom = df_hom['N_VICTIMAS'].groupby(df_hom['datetime'].dt.year).sum()[year]
except:
    totHom = df_hom['N_VICTIMAS'].sum()

# Create a base map centered around London
ba_map = folium.Map(width=350,height=450,location=[df_hom['pos y'].median()-0.025, df_hom['pos x'].median()+0.02], zoom_start=11)

# Add scatter plot points to the map
for _, row in df_hom[df_hom['pos x'].notnull()].iterrows():
    s,color,o = "4",'Yellow',"1"
    icontxt = "<div><svg><circle cx='50' cy='50' r=" + s + " fill=" + color + " opacity=" + o + "/></svg></div>"
    folium.Marker(location=[row['pos y'], row['pos x']],icon = folium.DivIcon(html=icontxt)).add_to(ba_map)

col1, col2, col3, col4, col5 = st.columns([5,1.5,1.5,1.8,1.5])

col1md1 = "<h1 style='text-align: center; font-size:30px;'>Road Accidents in Buenos Aires</h1>"
col1.markdown(col1md1, unsafe_allow_html=True)

col2md1 = "<h1 style='text-align: center; font-size:15px;'>Homicides</h1>"
col2.markdown(col2md1, unsafe_allow_html=True)
col2md2 = "<p style='text-align: center; font-size:18px;'>" + str(totHom) + "</p>"
col2.markdown(col2md2, unsafe_allow_html=True)

col3md1 = "<h1 style='text-align: center; font-size:15px;'>Homicide Rate</h1>"
col3.markdown(col3md1, unsafe_allow_html=True)
col3md2 = "<p style='text-align: center; font-size:18px;'>" + str(totHom) + "</p>"
col3.markdown(col3md2, unsafe_allow_html=True)

col4md1 = "<h1 style='text-align: center; font-size:15px;'>Motorbike Homicides</h1>"
col4.markdown(col4md1, unsafe_allow_html=True)
col4md2 = "<p style='text-align: center; font-size:18px;'>" + str(totHom) + "</p>"
col4.markdown(col4md2, unsafe_allow_html=True)

col5md1 = "<h1 style='text-align: center; font-size:15px;'>Disease Time</h1>"
col5.markdown(col5md1, unsafe_allow_html=True)
col5md2 = "<p style='text-align: center; font-size:18px;'>" + str(totHom) + "</p>"
col5.markdown(col5md2, unsafe_allow_html=True)

st.divider()

col6, col7, col8 = st.columns([4,3,3])

with col6:
    if st.checkbox('Show Map'):
        col6md1 = "<h1 style='text-align: left; font-size:15px;'>Homicide Map</h1>"
        col6.markdown(col6md1, unsafe_allow_html=True)
        folium_static(ba_map,width=350,height=430)
    st.bar_chart(df_hom.groupby(df_hom['TIPO_DE_CALLE'],as_index=False).count(),x='TIPO_DE_CALLE',y='ID')

with col7:
    st.bar_chart(df_hom.groupby(df_hom['TIPO_DE_CALLE'],as_index=False).count(),x='TIPO_DE_CALLE',y='ID',height=275)
    st.bar_chart(df_hom.groupby(df_hom['TIPO_DE_CALLE'],as_index=False).count(),x='TIPO_DE_CALLE',y='ID',height=275)

with col8:
    st.bar_chart(df_hom.groupby(df_hom['TIPO_DE_CALLE'],as_index=False).count(),x='TIPO_DE_CALLE',y='ID',height=275)
    st.bar_chart(df_hom.groupby(df_hom['TIPO_DE_CALLE'],as_index=False).count(),x='TIPO_DE_CALLE',y='ID',height=275)

