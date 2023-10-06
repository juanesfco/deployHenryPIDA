import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

df_hom = pd.read_csv('data/df_homicides.csv')

if st.checkbox('show data'):
    st.dataframe(df_hom)
    st.write('Te amo morocha')

# Create a base map centered around London
ba_map = folium.Map(width=400,height=350,location=[df_hom['pos y'].median()-0.025, df_hom['pos x'].median()+0.02], zoom_start=11)

# Add scatter plot points to the map
for _, row in df_hom[df_hom['pos x'].notnull()].iterrows():
    s,color,o = "4",'DarkRed',"1"
    icontxt = "<div><svg><circle cx='50' cy='50' r=" + s + " fill=" + color + " opacity=" + o + "/></svg></div>"
    folium.Marker(location=[row['pos y'], row['pos x']],icon = folium.DivIcon(html=icontxt)).add_to(ba_map)

if st.checkbox('prueba mapa'):
    folium_static(ba_map,width=400,height=330)
    st.write('hola')



