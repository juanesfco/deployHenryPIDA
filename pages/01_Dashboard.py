import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static

# Page Styling
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

# Sidebar definition (inputs)
with st.sidebar:
    years = list(range(2016,2022))
    semesters = []
    for y in years:
        semesters.append(str(y)+'_S1')
        semesters.append(str(y)+'_S2')
    periods = ['All Time'] + years + semesters
    period = st.selectbox('Choose a Period',periods, 0)
    tunits = st.selectbox('Choose a Unit for Disease Time',['Days','Hours'], 0)
    tunitsd = {'Days':24,'Hours':1}
    tunitsplot = st.selectbox('Choose a Time Unit for All Time Plots',['Year','Semester'], 0)
    centerPlot = st.selectbox('Choose a Plot for the Center',['Map','Street Type','By Sex'], 0)

# Load datasets
df_hom = pd.read_csv('data/df_homicides.csv',parse_dates=['datetime'])
df_hom['semester'] = df_hom['datetime'].dt.year.astype(str) + '_S' + (df_hom['datetime'].dt.quarter.isin([3,4]).astype(int)+1).astype(str)
df_vic = pd.read_csv('data/df_victims.csv',parse_dates=['FECHA_FALLECIMIENTO'])
df_vic['datetime'] = df_vic['FECHA_FALLECIMIENTO'] - pd.to_timedelta(df_vic['hrsUntilDisease'],unit='h')
df_vic['semester'] = df_vic['datetime'].dt.year.astype(str) + '_S' + (df_vic['datetime'].dt.quarter.isin([3,4]).astype(int)+1).astype(str)
df_dem = pd.read_excel('raw_data/TR_L_AX03.xlsx',sheet_name='TR_L_AX03')

# Calculate Total Homicides
if type(period) == int:
    totHomn = df_hom['N_VICTIMAS'].groupby(df_hom['datetime'].dt.year).sum()[period]
elif type(period) == str:
    try:
        totHomn = df_hom['N_VICTIMAS'].groupby(df_hom['semester']).sum()[period]
    except:
        totHomn = df_hom['N_VICTIMAS'].sum()

# Calculate RAHR
pop = {}
for y in years:
    df_pop = pd.read_excel('raw_data/PBP_CO1025.xls',sheet_name=str(y))
    pop[y] = df_pop.iloc[2,1]

if type(period) == int:
    rahrn = df_hom['N_VICTIMAS'].groupby(df_hom['datetime'].dt.year).sum()[period]/pop[period]*100000
elif type(period) == str:
    try:
        rahrn = df_hom['N_VICTIMAS'].groupby(df_hom['semester']).sum()[period]/pop[int(period[:4])]*100000
    except:
        rahrn = df_hom['N_VICTIMAS'].sum()/np.mean(list(pop.values()))*100000

# Calculate RAHM
df_hom_mot = df_hom[(df_hom['VICTIMA']=='MOTO') | (df_hom['VICTIMA']=='PEATON_MOTO') |(df_hom['ACUSADO']=='MOTO')]
if type(period) == int:
    rahmn = df_hom_mot['N_VICTIMAS'].groupby(df_hom_mot['datetime'].dt.year).sum()[period]
elif type(period) == str:
    try:
        rahmn = df_hom_mot['N_VICTIMAS'].groupby(df_hom_mot['semester']).sum()[period]
    except:
        rahmn = df_hom_mot['N_VICTIMAS'].sum()

# Calculate RAHDT
if type(period) == int:
    rahdtn = df_vic['hrsUntilDisease'].groupby(df_vic['datetime'].dt.year).mean()[period]/tunitsd[tunits]
elif type(period) == str:
    try:
        rahdtn = df_vic['hrsUntilDisease'].groupby(df_vic['semester']).mean()[period]/tunitsd[tunits]
    except:
        rahdtn = df_vic['hrsUntilDisease'].mean()/tunitsd[tunits]

# Calculate HomTime Df
if type(period) == int:
    df_hom_y = df_hom[df_hom['datetime'].dt.year == period]
    homTimes = df_hom_y['N_VICTIMAS'].groupby(df_hom_y['datetime'].dt.month).sum().values
    index = df_hom_y['N_VICTIMAS'].groupby(df_hom_y['datetime'].dt.month).sum().index
    df_homTime = pd.DataFrame({'Homicides':homTimes,'Month':index})
elif type(period) == str:
    if period != "All Time":
        df_hom_s = df_hom[df_hom['semester'] == period]
        homTimes = df_hom_s['N_VICTIMAS'].groupby(df_hom_s['datetime'].dt.day).sum().values
        index = df_hom_s['N_VICTIMAS'].groupby(df_hom_s['datetime'].dt.day).sum().index
        df_homTime = pd.DataFrame({'Homicides':homTimes,'Day':index})
    else:
        if tunitsplot == "Year":
            homTimes = df_hom['N_VICTIMAS'].groupby(df_hom['datetime'].dt.year).sum().values
            index = df_hom['N_VICTIMAS'].groupby(df_hom['datetime'].dt.year).sum().index
            df_homTime = pd.DataFrame({'Homicides':homTimes,'Year':index.astype(str)})
        else:
            homTimes = df_hom['N_VICTIMAS'].groupby(df_hom['semester']).sum().values
            index = df_hom['N_VICTIMAS'].groupby(df_hom['semester']).sum().index
            df_homTime = pd.DataFrame({'Homicides':homTimes,'Semester':index.astype(str)})

# Calculate HomRateTime Df
if type(period) == int:
    RAHR = []
    df_homy = df_hom[df_hom['datetime'].dt.year==period]
    for periodi in range(1,13):
        rahr = df_homy['N_VICTIMAS'].groupby(df_homy['datetime'].dt.month).sum()[periodi]/pop[period]*100000
        RAHR.append(rahr)
    objective = (len(np.array(range(1,13))))*[-10]
    df_homRateTime = pd.DataFrame({'Month':np.array(range(1,13)),'Homicide Rate':RAHR,'Objective':objective})
    df_homRateTime['HR Change %'] = df_homRateTime['Homicide Rate'].pct_change()*100
elif type(period) == str:
    if period != "All Time":
        RAHR = []
        df_homs = df_hom[df_hom['semester']==period]
        df_homs_gb = df_homs['N_VICTIMAS'].groupby(df_homs['datetime'].dt.day).sum()
        for periodi in df_homs_gb.index:
            rahr = df_homs_gb[periodi]/pop[int(period[:4])]*100000
            RAHR.append(rahr)
        objective = (len(df_homs_gb.index))*[-10]
        df_homRateTime = pd.DataFrame({'Day':df_homs_gb.index,'Homicide Rate':RAHR,'Objective':objective})
        df_homRateTime['HR Change %'] = df_homRateTime['Homicide Rate'].pct_change()*100
    else:
        if tunitsplot == "Year":
            RAHR = []
            for periodi in years:
                rahr = df_hom['N_VICTIMAS'].groupby(df_hom['datetime'].dt.year).sum()[periodi]/pop[periodi]*100000
                RAHR.append(rahr)
            objective = (len(years))*[-10]
            df_homRateTime = pd.DataFrame({'Year':np.array(years).astype(str),'Homicide Rate':RAHR,'Objective':objective})
            df_homRateTime['HR Change %'] = df_homRateTime['Homicide Rate'].pct_change()*100
        else:
            RAHR = []
            for periodi in semesters:
                rahr = df_hom['N_VICTIMAS'].groupby(df_hom['semester']).sum()[periodi]/pop[int(periodi[:4])]*100000
                RAHR.append(rahr)
            objective = (len(semesters))*[-10]
            df_homRateTime = pd.DataFrame({'Semester':np.array(semesters).astype(str),'Homicide Rate':RAHR,'Objective':objective})
            df_homRateTime['HR Change %'] = df_homRateTime['Homicide Rate'].pct_change()*100

# Calculate MotHomTime Df
if type(period) == int:
    RAHM = []
    df_hom_moty = df_hom_mot[df_hom_mot['datetime'].dt.year==period]
    df_hom_moty_gb = df_hom_moty['N_VICTIMAS'].groupby(df_hom_moty['datetime'].dt.month).sum()
    for periodi in df_hom_moty_gb.index:
        rahm = df_hom_moty_gb[periodi]
        RAHM.append(rahm)
    objective = (len(df_hom_moty_gb.index))*[-7]
    df_MotHomTime = pd.DataFrame({'Month':df_hom_moty_gb.index,'Motorbike Homicides':RAHM,'Objective':objective})
    df_MotHomTime['MH Change %'] = df_MotHomTime['Motorbike Homicides'].pct_change()*100
elif type(period) == str:
    if period != "All Time":
        RAHM = []
        df_hom_mots = df_hom_mot[df_hom_mot['semester']==period]
        df_hom_mots_gb = df_hom_mots['N_VICTIMAS'].groupby(df_homs['datetime'].dt.day).sum()
        for periodi in df_hom_mots_gb.index:
            rahm = df_hom_mots_gb[periodi]/pop[int(period[:4])]*100000
            RAHM.append(rahm)
        objective = (len(df_hom_mots_gb.index))*[-7]
        df_MotHomTime = pd.DataFrame({'Day':df_hom_mots_gb.index,'Motorbike Homicides':RAHM,'Objective':objective})
        df_MotHomTime['MH Change %'] = df_MotHomTime['Motorbike Homicides'].pct_change()*100
    else:
        if tunitsplot == "Year":
            RAHM = []
            for periodi in years:
                rahm = df_hom_mot['N_VICTIMAS'].groupby(df_hom_mot['datetime'].dt.year).sum()[periodi]
                RAHM.append(rahm)
            objective = (len(years))*[-7]
            df_MotHomTime = pd.DataFrame({'Year':np.array(years).astype(str),'Motorbike Homicides':RAHM,'Objective':objective})
            df_MotHomTime['MH Change %'] = df_MotHomTime['Motorbike Homicides'].pct_change()*100
        else:
            RAHM = []
            for periodi in semesters:
                rahm = df_hom_mot['N_VICTIMAS'].groupby(df_hom_mot['semester']).sum()[periodi]
                RAHM.append(rahm)
            objective = (len(semesters))*[-7]
            df_MotHomTime = pd.DataFrame({'Semester':np.array(semesters).astype(str),'Motorbike Homicides':RAHM,'Objective':objective})
            df_MotHomTime['MH Change %'] = df_MotHomTime['Motorbike Homicides'].pct_change()*100

# Calculate DTTime Df
if type(period) == int:
    RAHDT = []
    df_vicy = df_vic[df_vic['datetime'].dt.year==period]
    for periodi in range(1,13):
        rahdt = df_vicy['hrsUntilDisease'].groupby(df_vicy['datetime'].dt.month).mean()[periodi]/tunitsd[tunits]
        RAHDT.append(rahdt)
    objective = (len(np.array(range(1,13))))*[25]
    collab = 'Disease Time (' + tunits + ')'
    df_DTTime = pd.DataFrame({'Month':np.array(range(1,13)),collab:RAHDT,'Objective':objective})
    df_DTTime['DT Change %'] = df_DTTime[collab].pct_change()*100
elif type(period) == str:
    if period != "All Time":
        RAHDT = []
        df_vics = df_vic[df_vic['semester']==period]
        df_vics_gb = df_vics['hrsUntilDisease'].groupby(df_vics['datetime'].dt.day).mean()
        for periodi in df_vics_gb.index:
            rahdt = df_vics_gb[periodi]/tunitsd[tunits]
            RAHDT.append(rahdt)
        objective = (len(df_vics_gb.index))*[25]
        collab = 'Disease Time (' + tunits + ')'
        df_DTTime = pd.DataFrame({'Day':df_vics_gb.index,collab:RAHDT,'Objective':objective})
        df_DTTime['DT Change %'] = df_DTTime[collab].pct_change()*100
    else:
        if tunitsplot == "Year":
            RAHDT = []
            for periodi in years:
                rahdt = df_vic['hrsUntilDisease'].groupby(df_vic['datetime'].dt.year).mean()[periodi]/tunitsd[tunits]
                RAHDT.append(rahdt)
            objective = (len(years))*[25]
            collab = 'Disease Time (' + tunits + ')'
            df_DTTime = pd.DataFrame({'Year':np.array(years).astype(str),collab:RAHDT,'Objective':objective})
            df_DTTime['DT Change %'] = df_DTTime[collab].pct_change()*100
        else:
            RAHDT = []
            for periodi in semesters:
                rahdt = df_vic['hrsUntilDisease'].groupby(df_vic['semester']).mean()[periodi]/(tunitsd[tunits])
                RAHDT.append(rahdt)
            objective = (len(semesters))*[25]
            collab = 'Disease Time (' + tunits + ')'
            df_DTTime = pd.DataFrame({'Semester':np.array(semesters).astype(str),collab:RAHDT,'Objective':objective})
            df_DTTime['DT Change %'] = df_DTTime[collab].pct_change()*100

# Calculate bySex DF
licMale = df_dem.iloc[3,3] + df_dem.iloc[3,6]
licFemale = df_dem.iloc[3,4] + df_dem.iloc[3,7]
licTot = licMale + licFemale
if type(period) == int:
    df_sex = df_vic['SEXO'].groupby([df_vic['datetime'].dt.year,df_vic['SEXO']]).count().loc[period]
    ind = ['female_victims','female_drivers','male_victims','male_drivers']
    val = [df_sex.values[0]/sum(df_sex.values),licFemale/licTot,df_sex.values[1]/sum(df_sex.values),licMale/licTot]
    df_sex_f = pd.DataFrame({'SEXO':ind,'Density %':val})
elif type(period) == str:
    try:
        df_sex = df_vic['SEXO'].groupby([df_vic['semester'],df_vic['SEXO']]).count().loc[period]
        ind = ['female_victims','female_drivers','male_victims','male_drivers']
        val = [df_sex.values[0]/sum(df_sex.values),licFemale/licTot,df_sex.values[1]/sum(df_sex.values),licMale/licTot]
        df_sex_f = pd.DataFrame({'SEXO':ind,'Density %':val})
    except:
        df_sex = df_vic['SEXO'].groupby(df_vic['SEXO']).count()
        ind = ['female_victims','female_drivers','male_victims','male_drivers']
        val = [df_sex.values[0]/sum(df_sex.values),licFemale/licTot,df_sex.values[1]/sum(df_sex.values),licMale/licTot]
        df_sex_f = pd.DataFrame({'SEXO':ind,'Density %':val})

# Calculate Street Type DF
if type(period) == int:
    df_st = df_hom['TIPO_DE_CALLE'].groupby([df_hom['datetime'].dt.year,df_hom['TIPO_DE_CALLE']]).count().loc[period]
    df_st_f = pd.DataFrame({'TIPO_DE_CALLE':df_st.index,'Homicides':df_st.values})
elif type(period) == str:
    try:
        df_st = df_hom['TIPO_DE_CALLE'].groupby([df_hom['semester'],df_hom['TIPO_DE_CALLE']]).count().loc[period]
        df_st_f = pd.DataFrame({'TIPO_DE_CALLE':df_st.index,'Homicides':df_st.values})
    except:
        df_st = df_hom['TIPO_DE_CALLE'].groupby(df_hom['TIPO_DE_CALLE']).count()
        df_st_f = pd.DataFrame({'TIPO_DE_CALLE':df_st.index,'Homicides':df_st.values})

# Calculate Map DF
df_hom_nn = df_hom[df_hom['pos x'].notnull()]
if type(period) == int:
    df_hom_nn_fil = df_hom_nn[df_hom_nn['datetime'].dt.year==period]
    dflatlon = pd.DataFrame({'lat':df_hom_nn_fil['pos y'],'lon':df_hom_nn_fil['pos x']})
elif type(period) == str:
    if period != "All Time":
        df_hom_nn_fil = df_hom_nn[df_hom_nn['semester']==period]
        dflatlon = pd.DataFrame({'lat':df_hom_nn_fil['pos y'],'lon':df_hom_nn_fil['pos x']})
    else:
        dflatlon = pd.DataFrame({'lat':df_hom_nn['pos y'],'lon':df_hom_nn['pos x']})

#####################################################################

# Top Row Indicators
col1, col2, col3, col4, col5 = st.columns([5,1.5,1.5,1.8,1.5])

## Title
col1md1 = "<h1 style='text-align: center; background-color:#191D88; font-size:38px;'>Road Accidents in Buenos Aires</h1>"
col1.markdown(col1md1, unsafe_allow_html=True)

## Homicides
col2md1 = "<h1 style='text-align: center; background-color:#1450A3; font-size:15px;'>Homicides</h1>"
col2.markdown(col2md1, unsafe_allow_html=True)
col2md2 = "<p style='text-align: center; background-color:#1450A3; font-size:18px;'>" + str(totHomn) + "</p>"
col2.markdown(col2md2, unsafe_allow_html=True)

## RAHR
col3md1 = "<h1 style='text-align: center; background-color:#1450A3; font-size:15px;'>Homicide Rate</h1>"
col3.markdown(col3md1, unsafe_allow_html=True)
col3md2 = "<p style='text-align: center; background-color:#1450A3; font-size:18px;'>" + str(round(rahrn,3)) + "</p>"
col3.markdown(col3md2, unsafe_allow_html=True)

## RAHM
col4md1 = "<h1 style='text-align: center; background-color:#1450A3; font-size:15px;'>Motorbike Homicides</h1>"
col4.markdown(col4md1, unsafe_allow_html=True)
col4md2 = "<p style='text-align: center; background-color:#1450A3; font-size:18px;'>" + str(rahmn) + "</p>"
col4.markdown(col4md2, unsafe_allow_html=True)

## RAHDT
col5md1 = "<h1 style='text-align: center; background-color:#1450A3; font-size:15px;'>Disease Time</h1>"
col5.markdown(col5md1, unsafe_allow_html=True)
col5md2 = "<p style='text-align: center; background-color:#1450A3; font-size:18px;'>" + str(round(rahdtn,3)) + " " + tunits + "</p>"
col5.markdown(col5md2, unsafe_allow_html=True)

st.divider()

# Main Content
col6, col7, col8 = st.columns([3,4,3])

with col7:
    if centerPlot == 'By Sex':
        col7md1 = "<h1 style='text-align: center; background-color:#191D88; font-size:15px;'>Homicides by Sex</h1>"
        col7.markdown(col7md1, unsafe_allow_html=True)
        st.bar_chart(df_sex_f,x='SEXO',y=['Density %'],height=692,color='#FFC436')
    elif centerPlot == 'Street Type':
        col7md1 = "<h1 style='text-align: center; background-color:#191D88; font-size:15px;'>Homicides per Street Type</h1>"
        col7.markdown(col7md1, unsafe_allow_html=True)
        st.bar_chart(df_st_f,x='TIPO_DE_CALLE',y='Homicides',height=692,color='#FFC436')
    elif centerPlot == 'Map':
        col7md1 = "<h1 style='text-align: center; background-color:#191D88; font-size:15px;'>Homicide Map</h1>"
        col7.markdown(col7md1, unsafe_allow_html=True)
        st.map(dflatlon,color='#FFC436',zoom=10.5,use_container_width=True)
    

with col6:
    col6md1 = "<h1 style='text-align: center; background-color:#1450A3; font-size:15px;'>Homicides vs Time</h1>"
    col6.markdown(col6md1, unsafe_allow_html=True)
    if type(period) == int:
        st.area_chart(df_homTime,x='Month',y='Homicides',height=250,color='#FFC436')
    elif type(period) == str:
        if period != "All Time":
            st.area_chart(df_homTime,x='Day',y='Homicides',height=250,color='#FFC436')
        else:
            if tunitsplot == "Year":
                st.area_chart(df_homTime,x='Year',y='Homicides',height=250,color='#FFC436')
            else:
                st.area_chart(df_homTime,x='Semester',y='Homicides',height=250,color='#FFC436')
    col6md2 = "<h1 style='text-align: center; background-color:#1450A3; font-size:15px;'>Homicide Rate vs Time</h1>"
    col6.markdown(col6md2, unsafe_allow_html=True)
    if type(period) == int:
        st.line_chart(df_homRateTime,x='Month',y=['Homicide Rate','HR Change %','Objective'],height=400,color=['#1AACAC','#FFC436','#D83F31'])
    elif type(period) == str:
        if period != "All Time":
            st.line_chart(df_homRateTime,x='Day',y=['Homicide Rate','HR Change %','Objective'],height=400,color=['#1AACAC','#FFC436','#D83F31'])
        else:
            if tunitsplot == "Year":
                st.line_chart(df_homRateTime,x='Year',y=['Homicide Rate','HR Change %','Objective'],height=400,color=['#1AACAC','#FFC436','#D83F31'])
            else:
                st.line_chart(df_homRateTime,x='Semester',y=['Homicide Rate','HR Change %','Objective'],height=400,color=['#1AACAC','#FFC436','#D83F31'])

with col8:
    col8md1 = "<h1 style='text-align: center; background-color:#1450A3; font-size:15px;'>Motorbike Homicides vs Time</h1>"
    col8.markdown(col8md1, unsafe_allow_html=True)
    if type(period) == int:
        st.line_chart(df_MotHomTime,x='Month',y=['Motorbike Homicides','MH Change %','Objective'],height=320,color=['#1AACAC','#FFC436','#D83F31'])
    elif type(period) == str:
        if period != "All Time":
            st.line_chart(df_MotHomTime,x='Day',y=['Motorbike Homicides','MH Change %','Objective'],height=320,color=['#1AACAC','#FFC436','#D83F31'])
        else:
            if tunitsplot == "Year":
                st.line_chart(df_MotHomTime,x='Year',y=['Motorbike Homicides','MH Change %','Objective'],height=320,color=['#1AACAC','#FFC436','#D83F31'])
            else:
                st.line_chart(df_MotHomTime,x='Semester',y=['Motorbike Homicides','MH Change %','Objective'],height=320,color=['#1AACAC','#FFC436','#D83F31'])
    col8md2 = "<h1 style='text-align: center; background-color:#1450A3; font-size:15px;'>Disease Time vs Time</h1>"
    col8.markdown(col8md2, unsafe_allow_html=True)
    collab = 'Disease Time (' + tunits + ')'
    if type(period) == int:
        st.line_chart(df_DTTime,x='Month',y=[collab,'DT Change %','Objective'],height=320,color=['#1AACAC','#FFC436','#D83F31'])
    elif type(period) == str:
        if period != "All Time":
            st.line_chart(df_DTTime,x='Day',y=[collab,'DT Change %','Objective'],height=320,color=['#1AACAC','#FFC436','#D83F31'])
        else:
            if tunitsplot == "Year":
                st.line_chart(df_DTTime,x='Year',y=[collab,'DT Change %','Objective'],height=320,color=['#1AACAC','#FFC436','#D83F31'])
            else:
                st.line_chart(df_DTTime,x='Semester',y=[collab,'DT Change %','Objective'],height=320,color=['#1AACAC','#FFC436','#D83F31'])

