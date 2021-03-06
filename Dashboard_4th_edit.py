# -*- coding: utf-8 -*-
"""
Created on Tue Nov  2 08:56:33 2021

@author: IPSMX-L7NRKD03
"""

# Data load Package
#import io
from datetime import date

# Core Packages
import streamlit as st
from PIL import Image

# EDA Packages
import pandas as pd
import numpy as np

# Data Viz Packages
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objs as go

# ML Packages
# from sklearn.linear_model import LinearRegression
# Currency
#from forex_python.converter import CurrencyRates
#token = open("mapbox_token").read()

MM = 1000000
today = date.today() 

pd.options.mode.chained_assignment = None  # default='warn'

############################################################################################################################################################################################################

#################### CURRENCY ####################
#c = CurrencyRates()
#Currency = c.get_rate('USD', 'MXN')  #convert USD to MXN

#################### PAGE CONFIG ####################
APP_TITLE = "IPS Dashboard"
img=Image.open('Imagenes/IPS.png')
st.set_page_config(
    page_title = APP_TITLE,
    page_icon = img,
    layout = "wide")

img_sidebar= st.sidebar.columns(3)
img_sidebar[1].image(img,width=100)

############################################################################################################################################################################################################

#################### BARRIL ####################
metrics = pd.read_csv('Data/metrics.csv')
metrics = metrics.loc[:, ~metrics.columns.str.contains('^Unnamed')]
metrics.columns = [x.lower() for x in metrics.columns]
metrics['fecha'] = pd.to_datetime(metrics['fecha'])
metrics['fecha'] = metrics['fecha'].dt.strftime('%d-%m-%Y')
#metrics.index = metrics.fecha
#st.write(metrics['fecha'])

metrics_1 = pd.read_csv('Data/Barriles.csv')
metrics_1 = metrics_1.loc[:, ~metrics_1.columns.str.contains('^Unnamed')]
metrics_1.columns = [x.lower() for x in metrics_1.columns]
metrics_1['fecha'] = pd.to_datetime(metrics_1['fecha'])
metrics_1['fecha'] = metrics_1['fecha'].dt.strftime('%d-%m-%Y')



############################################################################################################################################################################################################

#################### PRODUCTION DATA ####################
prod = pd.read_csv('Data/Production Data.csv')
prod = prod.loc[:, ~prod.columns.str.contains('^Unnamed')]
prod.columns = [x.lower() for x in prod.columns]
prod['fecha'] = pd.to_datetime(prod['fecha'])
prod['lat'] = prod['lat'].astype(float)
prod['lon'] = prod['lon'].astype(float)

#################### PRESSURE DATA ####################
press = pd.read_csv('Data/Pressure Data.csv')
press = press.loc[:, ~press.columns.str.contains('^Unnamed')]
press.columns = [x.lower() for x in press.columns]
press['fecha'] = pd.to_datetime(press['fecha'])

#################### SALINITY DATA ####################
salt = pd.read_csv('Data/Salinity.csv')
salt = salt.loc[:, ~salt.columns.str.contains('^Unnamed')]
salt.columns = [x.lower() for x in salt.columns]
salt['fecha'] = pd.to_datetime(salt['fecha'])
salt.sort_values(by='fecha')
salt = salt.fillna(0)
salt = salt.rename(columns={"dens.": "densidad", "dens. m": "densidad_m"})
salt = salt.rename(columns={'pozo': 'terminacion', 'agua': 'water_cut'})
salt["salinidad"] = salt["salinidad"].astype('str')
salt['salinidad'] = salt['salinidad'].str.replace(',','')
salt['salinidad'] = salt['salinidad'].astype(float)
salt = salt[salt.salinidad >= 1]
salt = salt[salt.water_cut >= 1]

#################### TOPS DEPTH ####################
tops = pd.read_csv('Data/Layers.csv')
tops = tops.loc[:, ~tops.columns.str.contains('^Unnamed')]
tops.columns = [x.lower() for x in tops.columns]

############################################################################################################################################################################################################

#################### SIDEBAR ELEMENT 1 - DATA FILTER/SELECTORS ####################
with st.sidebar.expander('Field / Well Selector'):
    campos = prod['campo'].unique()
    filt_campos = st.selectbox('Select an oilfield', campos)
    
    campo = prod[prod['campo'] == filt_campos]
    
    pozos = campo['terminacion'].unique()
    filt_pozos = st.selectbox('Select a well', pozos)
    
    pozo = campo[campo['terminacion'] == filt_pozos]
    
#################### SIDEBAR ELEMENT 2 - DECLINATION CURVE ANALYTIC TOOLS ####################
with st.sidebar.expander('Declination Curve Analytics'):
    #di = st.sidebar.slider('Di value',0.0, 1.0, (0.130),0.005)
    di = st.number_input('Declination Index Value: ')
    capex = st.number_input('Enter a CAPEX value')
    opening = st.checkbox('CAPEX Reopen Well')
    interval = st.checkbox('CAPEX New Interval')
    reentry= st.checkbox('CAPEX Re-entry')
    
############################################################################################################################################################################################################

#################### SIDEBAR ELEMENT 2 - DECLINATION CURVE ANALYTIC TOOLS ####################
with st.sidebar.expander('Unit Converter'):
    st.subheader('Milion Cubit Feet to Cubic Meters')
    unit_1 = st.number_input('Enter a Value in Million Cubic Feet')
    st.write(str(round(unit_1*28316.85, 2)) + ' Cubic Meters')
    st.write(str(round(unit_1*28316.85/MM, 2)) + ' Million Cubic Meters')
    st.subheader('Barrel Price $ (MME)')
    barriles = st.number_input('Enter an amount of barrels')
    st.write(str(round(barriles*75.47, 2)) + ' USD')
    st.subheader('Dollars to Mexican Pesos')
    st.write(f'last available rate: {today}')
    dollars = st.number_input('Enter a value in US Dollars')
    st.write(str(round(dollars*20.32, 2)) + ' MXN')
    
#################### MAPA Y TABLA ####################

coords = prod[['campo','terminacion','lat', 'lon']]
coords['lat'] = pd.to_numeric(coords['lat'])
coords['lon'] = pd.to_numeric(coords['lon'])
coords = coords.dropna()

for_map = pozo.copy()
for_map = for_map[['campo', 'terminacion', 'fecha', 'class', 'lon', 'lat', 'aceite', 'gas', 'agua', 'aceite_bpd', 'agua_bpd', 'gas_mmcfpd', 'water_cut']]
for_map['fecha'] = for_map['fecha'].dt.date
map_filt = for_map.dropna()
map_filt['fecha'] = pd.to_datetime(map_filt['fecha'], dayfirst=True).dt.strftime('%m-%Y')

#################### SUBDATA POZOS ####################

r = pd.date_range(start=min(pozo.fecha), end = max(pozo.fecha), freq='M')
start = min(str(pozo.fecha))
pozo.index = pd.DatetimeIndex(pozo.fecha)
pozo = pozo.reindex(r, fill_value=0)
pozo['fecha'] = pozo.index
pozo['Mo'] = np.arange(len(pozo)) + 1
pozo['Yr'] = pozo['Mo'] / 12

f = pd.date_range(start='11/30/2021', end='12/31/2031', freq='M')

datad = np.random.randint(1, high=100, size=len(f))

# Copia del df -> pozo pero con nuevas columnas
pozo_2 = pd.DataFrame({'fecha': f, 'col2': datad})
pozo_2 = pozo_2.set_index('fecha')
pozo_2['Mo'] = np.arange(len(pozo_2)) + 1
pozo_2['Yr'] = pozo_2['Mo'] / 12
del pozo_2['col2']

# Calculos de acumulado
cum_oil = (pozo['aceite_bpd'].sum()*30.5)/MM
cum_gas = (pozo['gas'].sum()*30.5)/MM
cum_agua = (pozo['agua_bpd'].sum()*30.5)/MM

# Calculo de la curva de tendencia
pozo['Historical trend'] = max(pozo['aceite_bpd']) / (1 + 0.000000001 * di * pozo['Yr']) ** (1 /0.000000001)

# Calculo de nuevas columnas a 'pozo_2'
pozo_2['Open'] = 100 / (1 + 0.000000001 * di * pozo_2['Yr']) ** (1 /0.000000001)
pozo_2['Open_Interval'] = 202 / (1 + 0.000000001 * di * pozo_2['Yr']) ** (1 /0.000000001)
pozo_2['Reentry'] = 607 / (1 + 0.000000001 * di * pozo_2['Yr']) ** (1 /0.000000001)

pozo_2['Open'] = np.where(pozo_2['Open']<= 10 , np.nan, pozo_2['Open'])
pozo_2['Open_Interval'] = np.where(pozo_2['Open_Interval']<= 10 , np.nan, pozo_2['Open_Interval'])
pozo_2['Reentry'] = np.where(pozo_2['Reentry']<= 10 , np.nan, pozo_2['Reentry'])

pozo_2['Day'] = pozo_2.index.day
pozo_2['Month'] = pozo_2.index.month
pozo_2['Year'] = pozo_2.index.year

# Copia de df con mismos valores que 'pozo_2'
pozo_3 = pozo_2
pozo_4 = pozo_2

# Indexar fecha en las nuevas variables
pozo_3['Day'] = pozo_2.index.day
pozo_3['Month'] = pozo_2.index.month
pozo_3['Year'] = pozo_2.index.year
pozo_4['Day'] = pozo_2.index.day
pozo_4['Month'] = pozo_2.index.month
pozo_4['Year'] = pozo_2.index.year
pozo_2['Price'] = 60
pozo_2['Open_monthly'] = pozo_2['Open'] * pozo_2['Day']
pozo_2['Open_Interval_monthly'] = pozo_2['Open_Interval'] * pozo_2['Day']
pozo_2['Reentry_monthly'] = pozo_2['Reentry'] * pozo_2['Day']
pozo_2['Revenue_Open'] = 60 * pozo_2['Open'] * pozo_2['Day']
pozo_2['Revenue_Open_Interval'] = 60 * pozo_2['Open_Interval'] * pozo_2['Day'] 
pozo_2['Revenue_Reentry'] = 60 * pozo_2['Reentry'] * pozo_2['Day']

pozo_3 = pozo_2.groupby(["Year",'Month'], as_index=False)[['Open_monthly','Revenue_Open']].apply(sum)

pozo_4 = pozo_2.groupby(["Year",'Month'], as_index=False)[['Open_Interval_monthly','Revenue_Open_Interval']].apply(sum)

pozo_5 = pozo_2.groupby(["Year",'Month'], as_index=False)[['Reentry_monthly','Revenue_Reentry']].apply(sum)

#################### SUBDATA CAMPOS ####################
#del filtrado['water_cut']
campo.index = pd.DatetimeIndex(campo.fecha)
campo['Aceite_Anual'] = campo['aceite_bpd'] * campo['dias']
campo['Gas_Anual'] = campo['gas_cmpd'] * campo['dias']
campo['Agua_Anual'] = campo['agua_bpd'] * campo['dias']
campo['Day'] = campo.index.day
campo['Month'] = campo.index.month
campo['Year'] = campo.index.year
    
      
campo_2 = campo.groupby(["Year"], as_index=False)[['Aceite_Anual','Gas_Anual','Agua_Anual']].apply(sum) ###FIL###
campo_2['water_cut1'] = campo_2['Agua_Anual'] / (campo_2['Agua_Anual']+campo_2['Aceite_Anual']) 

cum_oil_camp = (campo_2['Aceite_Anual'].sum())/MM
cum_gas_camp = (campo_2['Gas_Anual'].sum())/MM
cum_agua_camp = (campo_2['Agua_Anual'].sum())/MM

#################### SUBDATA FIELD PRESSURE ####################
press_campo = press[press['campo'] == filt_campos]
press_campo.index = pd.DatetimeIndex(press_campo.fecha)
press_campo['Day'] = press_campo.index.day
press_campo['Month'] = press_campo.index.month
press_campo['Year'] = press_campo.index.year

press_campo_2 = press_campo.groupby(["Year"], as_index=False)[['cerrado(yac)', 'cerrado(pozo)', 'fluyendo(yac)', 'fluyendo(pozo)']].apply(sum) 
###FIL2###
#'cerrado(yac)', 'cerrado(pozo)', 'fluyendo(yac)', 'fluyendo(pozo)'#

#################### SUBDATA GOR/WOR 1 ####################
campo['GOR'] = campo['gas'] / campo['aceite_barrels']
campo['GOR+1'] = (campo['gas'] + campo['aceite_barrels']) / campo['aceite_barrels']
campo['WOR'] = campo['agua_bpm'] / campo['aceite_barrels']
campo['WOR+1'] = (campo['agua_bpm'] + campo['aceite_barrels']) / campo['aceite_barrels']
campo['cum_days'] = campo['dias'].cumsum()

#################### SUBDATA GOR/WOR 2 ####################
pozo['GOR'] = pozo['gas'] / pozo['aceite_barrels']
pozo['GOR+1'] = (pozo['gas'] + pozo['aceite_barrels']) / pozo['aceite_barrels']
pozo['WOR'] = pozo['agua_bpm'] / pozo['aceite_barrels']
pozo['WOR+1'] = (pozo['agua_bpm'] + pozo['aceite_barrels']) / pozo['aceite_barrels']
pozo['cum_days'] = pozo['dias'].cumsum()

#################### SUBDATA SALINITY ####################
salt_pozo = salt[salt['terminacion'] == filt_pozos]
salt_pozo.index = pd.DatetimeIndex(salt_pozo.fecha)
salt_pozo['Day'] = salt_pozo.index.day
salt_pozo['Month'] = salt_pozo.index.month
salt_pozo['Year'] = salt_pozo.index.year

salt_pozo_2 = salt_pozo.groupby(["Year"], as_index=False)[['salinidad', 'water_cut', 'densidad', 'densidad_m']].apply(sum)

#################### SUBDATA SALINITY 2 ####################
salt_campo = salt[salt['campo'] == filt_campos]
salt_campo.index = pd.DatetimeIndex(salt_campo.fecha)
salt_campo['Day'] = salt_campo.index.day
salt_campo['Month'] = salt_campo.index.month
salt_campo['Year'] = salt_campo.index.year
salt_campo = salt_campo.sort_index()

salt_campo_2 = salt_campo.groupby(["Year"], as_index=False)[['salinidad', 'water_cut', 'densidad', 'densidad_m']].apply(sum)

#################### BARRAS Y PIE #################### 
oilwells = prod.groupby(['terminacion']).sum()
oilwells = oilwells.sort_values(by=['aceite_barrels'])
oilwells = oilwells.nlargest(25, 'aceite_barrels').reset_index()

oilfields = prod.groupby(['campo']).sum()
oilfields = oilfields.sort_values(by=['aceite_barrels'])
oilfields = oilfields.nlargest(15, 'aceite_barrels').reset_index()

gaswells = prod.groupby(['terminacion']).sum()
gaswells = gaswells.sort_values(by=['gas'])
gaswells = gaswells.nlargest(25, 'gas').reset_index()

gasfields = prod.groupby(['campo']).sum()
gasfields = gasfields.sort_values(by=['gas'])
gasfields = gasfields.nlargest(15, 'gas').reset_index()

waterwells = prod.groupby(['terminacion']).sum()
waterwells = waterwells.sort_values(by=['agua'])
waterwells = waterwells.nlargest(25, 'agua').reset_index()

waterfields = prod.groupby(['campo']).sum()
waterfields = waterfields.sort_values(by=['agua_bpd'])
waterfields = waterfields.nlargest(15, 'agua_bpd').reset_index()
############################################################################################################################################################################################################

if st.checkbox('Show Tips') == True:
    st.caption('Welcome to our data visualization tool. We want to make sure that you get the best exprience from our dashboard so here are some tips:')
    st.caption('- Use Google Chrome preferably')
    st.caption('- If you are using a computer/laptop screen keep the zoom range to 100% (In your browser)')
    st.caption('- In case you are using a monitor: fix the zoom range to 125% or higher to see the plots fully sized')
    st.caption('- The current vesion of this tool takes some time to calculate data or even render the plots that are being displayed, we apologize if this may cause any inconvenience')
    st.caption('- The sidebar controls most of the dashboards functionalities, keep it open for a better experience')
    st.caption('- The main purpose of this dashboard is to visualize Macuspana-Muspac oildfields summarized information. Please select an specific field and well on the sidebar to generate plots of your selection')
    st.caption("- Keep in mind that at this moment due to the project's purpose we have only collected data from Sitio Grande oilfield")
    st.caption('- Dashboard Module: <<Project Economics/Declination Curve Analysis>> works with the sidebar panel Declination Curve Analytics')
    st.caption('- Some elements of this dashboard require an internet connection, i.e. maps. Also we have noticed a better performance when no more than three graphics are plotted at same time')
    st.caption('- We stongly recommend to always use a declination index of 12% (0.12) to calculate a realistic trend curve')
    st.caption('- Keep in mind that CAPEX values are presented in US Dollars (USD) or a fraction of Million US Dollars')
    st.caption('- This tool is a work in progress. We are always open to suggestions. If you have any comments about this tool please contact us at: jelaayi@ips-usa.net, vtorres@ips-mexico.com or jcluna@ips-mexico.com')
    
############################################################################################################################################################################################################
st.markdown("<h1 style='text-align: right; color: #132847;'> <b>Oil Economics</b></h1>", unsafe_allow_html=True)
with st.container():
    with st.expander('Oil Barrel Price Statistics (Mezcla Mexicana de Exportaci??n)'):
        #barrel_price_line = px.line(metrics, x=metrics.fecha, y=metrics.usd, width=1000, text='fecha')
        barrel_price_line = make_subplots(specs=[[{"secondary_y": False}]])
        barrel_price_line.add_trace(go.Scatter(x=metrics['fecha'], y=metrics['usd'], mode='lines', marker_line_width=.4, marker=dict(size=3, color='green')))
        # update trace
        barrel_price_line.update_traces(marker=dict(size=5, line=dict(width=.4, color='DarkSlateGrey')), selector=dict(mode='markers'))
        barrel_price_line.update_layout(title_text = 'Historical Price of the Mexican Oil Barrel')
        barrel_price_line.update_layout(hovermode="x unified")
        barrel_price_line.update_layout(margin={"r":0,"t":50,"l":0,"b":0}, height=400, width=1000)
        barrel_price_line.update_yaxes(title_text="US Dollars")
        barrel_price_line.update_yaxes(nticks=10)
        barrel_price_line.update_xaxes(nticks=35)
        st.plotly_chart(barrel_price_line)
        
        barrel_price = px.bar(metrics_1, x=metrics_1.fecha, y=metrics_1.usd, width=1000, color='usd')
        barrel_price.update_coloraxes(showscale=False)
        barrel_price.update_layout(margin={"r":0,"t":50,"l":0,"b":0}, height=400, width=1000)
        barrel_price.update_layout(hovermode="x unified")
        barrel_price.update_yaxes(title_text="US Dollars")
        barrel_price.update_yaxes(nticks=10)
        barrel_price.update_xaxes(title_text="Date")
        barrel_price.update_xaxes(nticks=35)
        st.plotly_chart(barrel_price)
        st.caption('This chart is the average calculation of all the sampled data available courtesy of BANXICO at: https://www.banxico.org.mx/apps/gc/precios-spot-del-petroleo-gra.html')
        cols_oilbar = st.columns(2)
        cols_oilbar[0].write(metrics.describe())
        cols_oilbar[0].write('Chart 1 Statistics')
        cols_oilbar[1].write(metrics_1.describe())
        cols_oilbar[1].write('Chart 2 Statistics')
        
st.markdown("<h1 style='text-align: right; color: #132847;'> <b>Project</b></h1>", unsafe_allow_html=True)

with st.container():
    #################### EXPANDER 1 - CHECK RAW DATA ####################
    with st.expander('Raw Data'):
        st.subheader('Data Loaded')
        st.write(prod)
        st.write(press)
        st.write(salt)
        st.write(tops)
    
    #################### EXPANDER 1 - PRODUCTION DATA PLOTS ####################
    with st.expander('Production Data Plots'):
        
        st.subheader('Well Location - Maps')
        
        map_selector = st.selectbox('Select a Category', ('Hide Map','All Wells and Fields', 'Selected Field Oil Production', 'Selected Field Gas Production', 'Selected Field Water Production', 'Selected Well'))
        
        map_pozos_loc = px.scatter_mapbox(prod, lat="lat", lon="lon", hover_name="terminacion", zoom=7.5, color='campo', color_discrete_sequence=px.colors.qualitative.Alphabet)
        map_pozos_loc.update_layout(mapbox_style="stamen-terrain", margin={"r":0,"t":0,"l":0,"b":0}, height=400, width=1000, showlegend=False)
        
        map_oil = px.scatter_mapbox(campo, lat="lat", lon="lon", hover_name="terminacion", zoom=10, size='aceite_bpd', color='aceite_bpd', color_continuous_scale=[(0,'#1fc600'),(1,'#0a5d00')], size_max=12)
        map_oil.update_layout(mapbox_style="stamen-terrain", margin={"r":0,"t":0,"l":0,"b":0}, height=400, width=1000)
        
        map_gas = px.scatter_mapbox(campo, lat="lat", lon="lon", hover_name="terminacion", zoom=10, size='gas_cmpd', color='gas_cmpd', color_continuous_scale=[(0,'#ee2400'),(1,'#900000')], size_max=12)
        map_gas.update_layout(mapbox_style="stamen-terrain", margin={"r":0,"t":0,"l":0,"b":0}, height=400, width=1000)
        
        map_water = px.scatter_mapbox(campo, lat="lat", lon="lon", hover_name="terminacion", zoom=10, size='agua_bpd', color='agua_bpd', color_continuous_scale=[(0,'#ADD8E6'),(1,'blue')], size_max=12)
        map_water.update_layout(mapbox_style="stamen-terrain", margin={"r":0,"t":0,"l":0,"b":0}, height=400, width=1000)
        
        map_pozo_loc = px.scatter_mapbox(pozo, lat="lat", lon="lon", hover_name="terminacion", zoom=5, color='campo')
        map_pozo_loc.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0}, height=400, width=1000, showlegend=False)
        
        if map_selector == 'Hide Map':
            st.write('')
        if map_selector == 'All Wells and Fields':
            st.map(coords)
        if map_selector == 'Selected Field Oil Production':
            st.plotly_chart(map_oil)
        if map_selector == 'Selected Field Gas Production':
            st.plotly_chart(map_gas)
        if map_selector == 'Selected Field Water Production':
            st.plotly_chart(map_water)
        if map_selector == 'Selected Well':
            st.plotly_chart(map_pozo_loc)
        
        # FIG 2 - DATOS HISTORICOS DEL CAMPO
        st.subheader('Historical Production Plots')
        
        prod_hist_select = st.selectbox('Well and Field Selected from the Sidebar', ('None', f'Historical Producion {filt_campos} Field', f'Historical Production {filt_pozos}'))
        
        field_prod = make_subplots(specs=[[{"secondary_y": True}]])
        field_prod.add_trace(go.Scatter(x=campo_2['Year'], y=campo_2['Aceite_Anual'], mode='lines+markers', marker_line_width=.5, marker=dict(size=4,color='green'),name='Oil'), secondary_y=False)
        field_prod.add_trace(go.Scatter(x=campo_2['Year'], y=campo_2['Agua_Anual'], mode='lines+markers', marker_line_width=.5, marker=dict(size=4,color='blue'), name='Water'), secondary_y=False)
        field_prod.add_trace(go.Scatter(x=campo_2['Year'], y=campo_2['Gas_Anual'], mode='lines+markers', marker_line_width=.5, marker=dict(size=4,color='red'),name='Gas'), secondary_y=True)
        # Set x-axis title
        field_prod.update_layout(hovermode="x unified")
        field_prod.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1))
        field_prod.update_xaxes(title_text="<b>Year</b>")
        field_prod.update_layout(margin={"r":0,"t":50,"l":0,"b":0}, height=400, width=1000)
        # Update
        field_prod.update_yaxes(title_text="<b>Oil [bbls] / Water Production [bbls]</b> ", secondary_y=False)
        field_prod.update_yaxes(title_text="<b>Gas Production Rate [Cubic Meters] </b>", secondary_y=True)
        field_prod.update_yaxes(nticks=25,secondary_y=False)
        field_prod.update_yaxes(nticks=25,secondary_y=True)
        field_prod.update_xaxes(nticks=10)
            
        # FIG 3 - DATOS HISTORICOS DEL POZO
        well_prod = make_subplots(specs=[[{"secondary_y": True}]])
        well_prod.add_trace(go.Scatter(x=pozo['fecha'], y=pozo['aceite_bpd'], mode='lines+markers', marker_line_width=.5, marker=dict(size=4,color='green'),name='Oil'),secondary_y=False)
        well_prod.add_trace(go.Scatter(x=pozo['fecha'], y=pozo['agua_bpd'], mode='lines+markers', marker_line_width=.5, marker=dict(size=4,color='blue'), name='Water'), secondary_y=False)
        well_prod.add_trace(go.Scatter(x=pozo['fecha'], y=pozo['gas'], mode='lines+markers', marker_line_width=.5, marker=dict(size=4,color='red'),name='Gas'),secondary_y=True)
    
        # Set layout
        well_prod.update_layout(title_text = f'Historical Production {filt_pozos}')
        well_prod.update_layout(hovermode="x unified")
        well_prod.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1))
        well_prod.update_layout(margin={"r":0,"t":50,"l":0,"b":0}, height=400, width=1000)
        # update x and y - axis
        well_prod.update_yaxes(title_text="<b>Oil Production Rate [bbls] / Water Production Rate [bbls] </b> ", secondary_y=False)
        well_prod.update_yaxes(title_text="<b> Gas Production Rate [Cubic Meters] </b>", secondary_y=True)
        well_prod.update_yaxes(nticks=10,secondary_y=False)
        well_prod.update_yaxes(nticks=10,secondary_y=True)
        well_prod.update_xaxes(title_text="<b>Year</b>")
        well_prod.update_xaxes(nticks=35)
        
        if prod_hist_select == 'None':
            st.write(' ')
            
        if prod_hist_select == f'Historical Producion {filt_campos} Field':
            st.plotly_chart(field_prod)
            st.caption("Cum Oil: " + str(round(cum_oil_camp,2)) + " MMBO")
            st.caption("Cum Gas: " + str(round(cum_gas_camp,2)) + " MMCMPD")
            st.caption("Cum Water: " + str(round(cum_agua_camp,2)) + " MMBO")
            
        if prod_hist_select == f'Historical Production {filt_pozos}':
            st.plotly_chart(well_prod)
            st.caption("Cum Oil: " + str(round(cum_oil,2)) + " MMBO")
            st.caption("Cum Gas: " + str(round(cum_gas,2)) + " MMCMPD")
            st.caption("Cum Water: " + str(round(cum_agua,2)) + " MMBO")
        
    #################### EXPANDER 1 - PRODUCTION DATA PLOTS ####################
        
        st.subheader('Well Plots')
        ##OIL##
        oil = px.scatter(campo, x= campo.index, y="aceite_bpd", log_y=False, color="terminacion")
        
        # update layout
        oil.update_layout(title=f'<b>Oil Production - {filt_campos}</b>', height=370, width=500)
        # update trace
        oil.update_traces(marker=dict(size=6, line=dict(width=.4, color='DarkSlateGrey')), selector=dict(mode='markers'))
        # update axis
        oil.update_yaxes(title_text="<b>Oil (BOPD)</b>", nticks=10)
        oil.update_xaxes(title_text="<b>Year</b>", nticks=20)  
        
        ##GAS##
        gas = px.scatter(campo, x= campo.index, y="gas", log_y=False, color="terminacion")
        
        # update layout
        gas.update_layout(title=f'<b>Gas Production - {filt_campos}</b>', height=370, width=500)
        # update trace
        gas.update_traces(marker=dict(size=6, line=dict(width=.4, color='DarkSlateGrey')), selector=dict(mode='markers'))
        # update axis
        gas.update_yaxes(title_text="<b>Gas (Cubic Meters per Day)</b>", nticks=10)
        gas.update_xaxes(title_text="<b>Year</b>", nticks=15)
        
        ##WATER##
        w_prod = px.scatter(campo, x= campo.index, y="agua_bpd", log_y=False, color="terminacion")
        
        # update layout
        w_prod.update_layout(title=f'<b>Water Production - {filt_campos}</b>', height=370, width=500)
        # update trace
        w_prod.update_traces(marker=dict(size=6, line=dict(width=.4, color='DarkSlateGrey')), selector=dict(mode='markers'))
        # update axis
        w_prod.update_yaxes(title_text="<b>Water Production (Barrels Per Day)</b>", nticks=10)
        w_prod.update_xaxes(title_text="<b>Year</b>", nticks=15)
        
        ##WATER CUT##
        w_cut = px.scatter(campo, x= campo.index, y="water_cut", log_y=False, color="terminacion")
        
        # update trace
        w_cut.update_traces(marker=dict(size=6, line=dict(width=.4, color='DarkSlateGrey')), selector=dict(mode='markers'))
        # update layout
        w_cut.update_layout(title=f'<b>Water Cut - {filt_campos}</b>', height=370, width=500)
        # update axis
        w_cut.update_yaxes(title_text="<b>Water Cut (%)</b>", nticks=10)
        w_cut.update_xaxes(title_text="<b>Year</b>", nticks=15)
        
        ##PRESS1##
        press_1 = px.scatter(press_campo, x= press_campo.index, y="cerrado(yac)", log_y=False, color="terminacion")
        
        # update trace
        press_1.update_traces(marker=dict(size=6, line=dict(width=.4, color='DarkSlateGrey')), selector=dict(mode='markers'))
        # update layout
        press_1.update_layout(title=f'<b>Reservoir Pressure (Plugged) - {filt_campos}</b>', height=370, width=500)
        # update axis
        press_1.update_yaxes(title_text="<b>Pressure (Kg/cm3)</b>", nticks=10)
        press_1.update_xaxes(title_text="<b>Year</b>", nticks=15)
        
        ##PRESS2##
        press_2 = px.scatter(press_campo, x= press_campo.index, y="cerrado(pozo)", log_y=False, color="terminacion")
        
        # update trace
        press_2.update_traces(marker=dict(size=6, line=dict(width=.4, color='DarkSlateGrey')), selector=dict(mode='markers'))
        # update layout
        press_2.update_layout(title=f'<b>Well Pressure (Plugged) - {filt_campos}</b>', height=370, width=500)
        # update axis
        press_2.update_yaxes(title_text="<b>Pressure (Kg/cm3)</b>", nticks=10)
        press_2.update_xaxes(title_text="<b>Year</b>", nticks=15)
        
        ##PRESS3##
        press_3 = px.scatter(press_campo, x= press_campo.index, y='fluyendo(yac)', log_y=False, color="terminacion")
        
        # update trace
        press_3.update_traces(marker=dict(size=6, line=dict(width=.4, color='DarkSlateGrey')), selector=dict(mode='markers'))
        # update layout
        press_3.update_layout(title=f'<b>Reservoir Pressure - {filt_campos}</b>', height=370, width=500)
        # update axis
        press_3.update_yaxes(title_text="<b>Pressure (Kg/cm3)</b>", nticks=10)
        press_3.update_xaxes(title_text="<b>Year</b>", nticks=15)
        
        ##PRESS4##
        press_4 = px.scatter(press_campo, x= press_campo.index, y='fluyendo(pozo)', log_y=False, color="terminacion")
        
        # update trace
        press_4.update_traces(marker=dict(size=6, line=dict(width=.4, color='DarkSlateGrey')), selector=dict(mode='markers'))
        # update layout
        press_4.update_layout(title=f'<b>Well Pressure - {filt_campos}</b>', height=370, width=500)
        # update axis
        press_4.update_yaxes(title_text="<b>Pressure (Kg/cm3)</b>", nticks=10)
        press_4.update_xaxes(title_text="<b>Year</b>", nticks=15)
    
        cols0 = st.columns(2)
        prod_plot_selector = cols0[0].selectbox('Production Plots', ('None', 'Oil (bbls/d)', 'Gas (cmpd)', 'Water (bbls/d)', 'Water Cut (%)'))
        if prod_plot_selector == 'None':
            cols0[0].write('')
        if prod_plot_selector == 'Oil (bbls/d)':
            cols0[0].plotly_chart(oil)
        if prod_plot_selector == 'Gas (cmpd)':
            cols0[0].plotly_chart(gas)
        if prod_plot_selector == 'Water (bbls/d)':
            cols0[0].plotly_chart(w_prod)
        if prod_plot_selector == 'Water Cut (%)':
            cols0[0].plotly_chart(w_cut)
            
        press_plot_selector = cols0[1].selectbox('Pressure Plots', ('None', 'Reservoir Pressure - Plugged (Kg/cm3)', 'Well Pressure - Plugged (Kg/cm3)', 'Reservoir Pressure (Kg/cm3)', 'Well Pressure (Kg/cm3)'))
        if press_plot_selector == 'None':
            cols0[1].write('')
        if press_plot_selector == 'Reservoir Pressure - Plugged (Kg/cm3)':
            cols0[1].plotly_chart(press_1)
        if press_plot_selector == 'Well Pressure - Plugged (Kg/cm3)':
            cols0[1].plotly_chart(press_2)
        if press_plot_selector == 'Reservoir Pressure (Kg/cm3)':
            cols0[1].plotly_chart(press_3)
        if press_plot_selector == 'Well Pressure (Kg/cm3)':
            cols0[1].plotly_chart(press_4)
    ############################################################################################################################################################################################################
    
    with st.expander('Project Economics / Declination Curve Analysis'):
        st.markdown(f"<h1 style='text-align: center; color: #132847;'> <b>{filt_pozos}</b></h1>", unsafe_allow_html=True)
        dec_curve = make_subplots(specs=[[{"secondary_y": True}]])
    
        dec_curve.add_trace(go.Scatter(x=pozo['fecha'], y=pozo['aceite_bpd'], mode='lines+markers', marker_line_width=.3, marker=dict(size=3,color='green'),name='OIL'), secondary_y=False)
        dec_curve.add_trace(go.Scatter(x=pozo['fecha'], y=pozo['gas_cmpd'], mode='lines+markers', marker_line_width=.3, marker=dict(size=3,color='red'), name='GAS'),secondary_y=True)
        dec_curve.add_trace(go.Scatter(x=pozo['fecha'], y=pozo['agua_bpd'], mode='lines+markers', marker_line_width=.3, marker=dict(size=3,color='blue'),name='WATER'), secondary_y=False)
        
        dec_curve.add_trace(go.Scatter(x=pozo_2.index, y=pozo_2['Open'], mode='markers', marker_line_width=.5, marker=dict(size=5,color='purple'), name='Open'), secondary_y=False)
        dec_curve.add_trace(go.Scatter(x=pozo_2.index, y=pozo_2['Open_Interval'], mode='markers', marker_line_width=.5, marker=dict(size=5,color='orange'),name='Open Interval'), secondary_y=False)
        dec_curve.add_trace(go.Scatter(x=pozo_2.index, y=pozo_2['Reentry'], mode='markers', marker_line_width=.5, marker=dict(size=5,color='cyan'), name='Reentry'),secondary_y=False)
        
        dec_curve.add_trace(go.Scatter(x=pozo['fecha'], y=pozo['Historical trend'], mode='markers', marker_line_width=.5, marker=dict(size=2,color='black'), name='Trend'), secondary_y=False)
    
        dec_curve.update_layout(hovermode="x unified")
        dec_curve.update_layout(margin={"r":0,"t":50,"l":0,"b":0}, height=500, width=1000)
        dec_curve.update_xaxes(title_text="<b>Year</b>")
        dec_curve.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
        # Set y-axes titles
        #dec_curve.update_layout(yaxis1=dict(type='log'))
        # update
        dec_curve.update_yaxes(title_text="<b>Oil [bbls] / Water Production [bbls]</b> ", secondary_y=False)
        dec_curve.update_yaxes(title_text="<b>Gas Production Rate [Cubic Meters]</b>", secondary_y=True)
        dec_curve.update_yaxes(nticks=20,secondary_y=False)
        dec_curve.update_yaxes(nticks=20,secondary_y=True)
        dec_curve.update_xaxes(nticks=25)
    
        st.plotly_chart(dec_curve)
        st.caption("Cum Oil: " + str(round(cum_oil,2)) + " MMBO")
        st.caption("Cum Gas: " + str(round(cum_gas,2)) + " MMCMPD")
        st.caption("Cum Water: " + str(round(cum_agua,2)) + " MMBO")
        st.write('')
        
        pozo_stats = pozo[['fecha', 'aceite_bpd', 'gas_cmpd', 'agua_bpd', 'Historical trend']]
        economic_stats = pozo_2[['Open', 'Open_Interval', 'Reentry']]
        
        if st.checkbox('Get Well Statistics') == True:
            st.write(pozo_stats.describe())
                
        col1,col2,col3 = st.columns(3)
    
    with st.container():
        with col1:
            col1.subheader("Re-open well")
            pozo_3.reset_index(drop=True, inplace=True)
            pozo_3['CAPEX'] = 0
            pozo_3.at[0,'CAPEX']= capex
            pozo_3['Cost'] = pozo_3['Revenue_Open'] - pozo_3['CAPEX']
            pozo_3['SumCost']=pozo_3['Cost'].cumsum()
            st.dataframe(pozo_3.style.format({"Revenue_Open": "{:,.0f}", "Revenue_Open_Interval": "{:,.0f}", "Revenue_Reentry": "{:,.0f}","Yr": "{:,.2f}","Open_monthly": "{:,.0f}","Open_Interval": "{:,.0f}","Reentry": "{:,.0f}"}))
            st.caption('Cum barrels: ' + str(round((pozo_3['Open_monthly'].sum()/MM),2)) + ' MMBO')
            st.caption('Cum Gross Revenue: ' + str(round((pozo_3['Revenue_Open'].sum()/MM),2)) + ' MM USD')
            if opening:
                net = (pozo_3['Revenue_Open'].sum()- capex)
                st.caption('Net Revenue: ' + str(round(net/MM,2)) + ' MM USD')
        with col2:
            col2.subheader("Open a New Interval")
            st.dataframe(pozo_4.style.format({"Revenue_Open": "{:,.0f}", "Revenue_Open_Interval": "{:,.0f}", "Revenue_Reentry": "{:,.0f}","Yr": "{:,.2f}","Open": "{:,.0f}","Open_Interval_monthly": "{:,.0f}","Reentry": "{:,.0f}"}))
        #st.dataframe(data5.style.format({"Revenue_Open": "{:,.0f}", "Revenue_Open_Interval": "{:,.0f}", "Revenue_Reentry": "{:,.0f}","Yr": "{:,.2f}","Open": "{:,.0f}","Open_Interval": "{:,.0f}","Reentry": "{:,.0f}"}))
            st.caption('Cum barrels: ' + str(round((pozo_4['Open_Interval_monthly'].sum()/MM),2)) + ' MMBO')
            st.caption('Cum Gross Revenue: ' + str(round((pozo_4['Revenue_Open_Interval'].sum()/MM),2)) + ' MM USD')
            if interval:
                net = (pozo_4['Revenue_Open_Interval'].sum()- capex)
                st.caption('Net Revenue: ' + str(round(net/MM,2)) + ' MM USD')
        with col3:
            col3.subheader("Re-Entry")
            st.dataframe(pozo_5.style.format({"Revenue_Open": "{:,.0f}", "Revenue_Open_Interval": "{:,.0f}", "Revenue_Reentry": "{:,.0f}","Yr": "{:,.2f}","Open": "{:,.0f}","Open_Interval": "{:,.0f}","Reentry_monthly": "{:,.0f}"}))
            st.caption('Cum barrels: ' + str(round((pozo_5['Reentry_monthly'].sum()/MM),2)) + ' MMBO')
            st.caption('Cum Gross Revenue: ' + str(round((pozo_5['Revenue_Reentry'].sum()/MM),2)) + ' MM USD')
            if reentry:
                net = (pozo_5['Revenue_Reentry'].sum()- capex)
                st.caption('Net Revenue: ' + str(round(net/MM,2)) + ' MM USD')
    
    ############################################################################################################################################################################################################
    with st.expander('Water Control Diagnostic Plots'):
        
        st.subheader('GOR/WOR Plots')
        
        gor_wor_select = st.selectbox('Options', ('None', 'Historical WOR', 'Historical GOR', 'Chan Plot WOR', 'Chan Plot GOR'))
        
        field_wor = px.scatter(campo, x=campo.index, y="WOR", color="terminacion", height=400, width=1000)
        field_wor.update_traces(marker=dict(size=5, line=dict(width=.5)), selector=dict(mode='markers'))
        # Set x-axis title
        field_wor.update_xaxes(title_text= "<b>Year</b>")
        # Update
        field_wor.update_layout(title_text=f'Historical WOR {filt_campos} Field')
        field_wor.update_yaxes(title_text="<b>WOR</b>")
        field_wor.update_yaxes(nticks=10,color = 'black')
        field_wor.update_xaxes(nticks=20,color = 'black', calendar = 'gregorian')
            
        field_gor = px.scatter(campo, x=campo.index, y="GOR", color="terminacion", height=400, width=1000)
        field_gor.update_traces(marker=dict(size=5, line=dict(width=.5)), selector=dict(mode='markers'))
        # Set x-axis title
        field_gor.update_xaxes(title_text= "<b>Year</b>")
        # Update
        field_gor.update_layout(title_text=f'Historical GOR {filt_campos} Field')
        field_gor.update_yaxes(title_text="<b>GOR</b>")
        field_gor.update_yaxes(nticks=10,color = 'black')
        field_gor.update_xaxes(nticks=20,color = 'black', calendar = 'gregorian')
            
        #################### Chan Plots ####################
        
        wor = make_subplots(specs=[[{"secondary_y": False}]])
        wor.add_trace(go.Scatter(x=pozo['fecha'], y=pozo['WOR'], mode='markers', marker_line_width=.3, marker=dict(size=4,color='skyblue'), name= 'WOR'))
        wor.add_trace(go.Scatter(x=pozo.cum_days, y=pozo['WOR+1'], mode='markers', marker_line_width=.3, marker=dict(size=4,color='darkblue'), name= 'WOR+1'))
        # Set x-axis title
        wor.update_layout(hovermode="x unified")
        wor.update_xaxes(title_text="<b>Days</b>")
        wor.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
        # update
        wor.update_layout(title_text=f'Chan plot {filt_pozos}', height=400, width=1000)
        wor.update_yaxes(title_text="<b>WOR/WOR'</b>")
        wor.update_yaxes(nticks=10)
        wor.update_yaxes(type="log")
        wor.update_xaxes(type="log")
        
        gor = make_subplots(specs=[[{"secondary_y": False}]])
        gor.add_trace(go.Scatter(x=pozo['fecha'], y=pozo['GOR'], mode='markers', marker_line_width=.3, marker=dict(size=4, color='red'), name= 'GOR'))
        gor.add_trace(go.Scatter(x=pozo.cum_days, y=pozo['GOR+1'], mode='markers', marker_line_width=.3, marker=dict(size=4, color='darkred'), name= 'GOR+1'))
        # update trace
        gor.update_traces(marker=dict(size=5, line=dict(width=.4, color='DarkSlateGrey')), selector=dict(mode='markers'))
        # Set x-axis title
        gor.update_layout(hovermode="x unified")
        gor.update_xaxes(title_text="<b>Days</b>")
        gor.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
        # update
        gor.update_layout(title_text=f'Chan plot {filt_pozos}', height=400, width=1000)
        gor.update_yaxes(title_text="<b>GOR/GOR'</b>")
        gor.update_yaxes(nticks=9)
        gor.update_yaxes(type="log")
        gor.update_xaxes(type="log")
        
        if gor_wor_select == 'None':
            st.write(' ')
        if gor_wor_select == 'Historical WOR':
            st.plotly_chart(field_wor)
        if gor_wor_select == 'Historical GOR':
            st.plotly_chart(field_gor)
        if gor_wor_select == 'Chan Plot WOR':
            st.plotly_chart(wor)
        if gor_wor_select == 'Chan Plot GOR':
            st.plotly_chart(gor)
            
        st.subheader('Salinity Plots')
        
        salt_hist_select = st.selectbox('Well and Field Selected from the Sidebar', ('None', f'Historical Salinity {filt_campos} Field', f'Historical Salinity {filt_pozos}'))
        
        #Field Salinity#
        salt_1 = st.columns(2)
        salt_camp_lines = px.line(salt_campo, x=salt_campo.index, y="salinidad", color="terminacion", height= 400, width=500)
        salt_camp_lines.update_traces(marker=dict(size=5, line=dict(width=.5)), selector=dict(mode='markers'))
        # Set x-axis title
        salt_camp_lines.update_layout(hovermode= "x unified")
        salt_camp_lines.update_xaxes(title_text= "<b>Year</b>")
        # Set y-axes titles
        #salt_camp.update_layout(yaxis1=dict(type='log'))
        # update
        salt_camp_lines.update_layout(title_text=f'Historical Salinity {filt_campos} Field')
        salt_camp_lines.update_yaxes(title_text="<b>Salinity (PPM)</b>")
        salt_camp_lines.update_yaxes(nticks=20,color = 'black')
        salt_camp_lines.update_xaxes(nticks=20,color = 'black', calendar = 'gregorian')
        
        salt_camp_dots = px.scatter(salt_campo, x=salt_campo.index, y="salinidad", color="terminacion", height= 400, width=500)
        salt_camp_dots.update_traces(marker=dict(size=5, line=dict(width=.5)), selector=dict(mode='markers'))
        # Set x-axis title
        salt_camp_dots.update_layout(hovermode= "x unified")
        salt_camp_dots.update_xaxes(title_text= "<b>Year</b>")
        # Set y-axes titles
        #salt_camp.update_layout(yaxis1=dict(type='log'))
        # update
        salt_camp_dots.update_layout(title_text=f'Historical Salinity {filt_campos} Field')
        salt_camp_dots.update_yaxes(title_text="<b>Salinity (PPM)</b>")
        salt_camp_dots.update_yaxes(nticks=20,color = 'black')
        salt_camp_dots.update_xaxes(nticks=20,color = 'black', calendar = 'gregorian')
        
        #Well Salinity#
        salt_well = make_subplots(specs=[[{"secondary_y": True}]])
        salt_well.add_trace(go.Scatter(x=salt_pozo['fecha'],y=salt_pozo['salinidad'], mode='lines+markers', marker_line_width=.3, marker=dict(size=3,color='purple'),name='Salinity'), secondary_y=False)
        salt_well.add_trace(go.Scatter(x=salt_pozo['fecha'],y=salt_pozo['water_cut'],mode='lines+markers', marker_line_width=.3,marker=dict(size=3,color='blue'),name='Water<br>Cut'), secondary_y=True)
        # Set x-axis title
        salt_well.update_layout(title=f'Historical Salinity {filt_pozos}', hovermode="x unified")
        salt_well.update_xaxes(title_text="<b>Year</b>")
        salt_well.update_layout(margin={"r":0,"t":50,"l":0,"b":0}, height=400, width=1000)
        # Set y-axes titles
        #salt_well.update_layout(yaxis1=dict(type='log'))
        # update
        salt_well.update_yaxes(title_text="<b>Salinity (PPM)</b> ", secondary_y=False)
        salt_well.update_yaxes(title_text="<b>Fw %</b>", secondary_y=True)
        salt_well.update_yaxes(nticks=20,secondary_y=False)
        salt_well.update_yaxes(nticks=20,secondary_y=True)
        salt_well.update_xaxes(nticks=20, calendar = 'gregorian')
        
        if salt_hist_select == 'None':
            st.write(' ')
        if salt_hist_select == f'Historical Salinity {filt_campos} Field':
            salt_1[0].plotly_chart(salt_camp_lines)
            salt_1[1].plotly_chart(salt_camp_dots)
        if salt_hist_select == f'Historical Salinity {filt_pozos}':
            st.plotly_chart(salt_well)
        
    ############################################################################################################################################################################################################
    
    #################### EXPANDER 3 - DATA ANALYTICS PLOTS #################### 
    with st.expander('Data Analytics'):
        data_stats_selector = st.selectbox('Data Statistics', ('None', 'Oil Production Statistics', 'Gas Production Statistics', 'Water Production Statistics'))
        if data_stats_selector == 'None':
            st.write(' ')
            
        if data_stats_selector == 'Oil Production Statistics':
            #OIL#
            bars_top_ten_oil = px.bar(oilfields, x='campo', y='aceite_barrels', labels={'Well':'Oil Production'}, height=400, width=1000)
            bars_top_ten_oil.update_xaxes(title_text="Oilfield")
            bars_top_ten_oil.update_yaxes(title_text="Total Oil Produced (BOPD)")
            bars_top_ten_oil.update_traces(marker_color='#82a1b8', marker_line_color='#132847', marker_line_width=1.5, opacity=0.6)
            bars_top_ten_oil.update_layout(title_text='Top 15 Oil Producer Fields')
            
            bars_top_ten_oilwell = px.bar(oilwells, x='aceite_barrels', y='terminacion', labels={'Well':'Oil Production'}, orientation='h', color='aceite_barrels', color_continuous_scale='RdBu')
            bars_top_ten_oilwell.update_xaxes(title_text="Oil [bbls/d]")
            bars_top_ten_oilwell.update_yaxes(title_text="Well")
            bars_top_ten_oilwell.update_layout(title_text='Top 25 Oil Producer Wells', yaxis={'categoryorder':'total ascending'}, yaxis_tickangle=-40)
            bars_top_ten_oilwell.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', width=500)    
            bars_top_ten_oilwell.update_traces(texttemplate='%{x:.2s}', textposition='auto')
            bars_top_ten_oilwell.update_coloraxes(showscale=False)
            
            pie_oil = px.pie(oilfields, names='campo', values='aceite_barrels', color='campo', color_discrete_sequence=px.colors.sequential.RdBu, title='Accumulated Oil Production (Field)', width=500)
            pie_oil.update_traces(textposition='inside', textinfo='percent+label', textfont_size=7)
            pie_oil.update_layout(uniformtext_minsize=7, showlegend=False)
            
            st.plotly_chart(bars_top_ten_oil)
            bars_pie_oil = st.columns(2)
            bars_pie_oil[0].plotly_chart(pie_oil)
            bars_pie_oil[1].plotly_chart(bars_top_ten_oilwell)    
        
        if data_stats_selector == 'Gas Production Statistics':
            #GAS#
            bars_top_ten_gas = px.bar(gasfields, x='campo', y='gas_mmcfpd', labels={'Well':'Gas Production'}, height=400, width=1000)
            bars_top_ten_gas.update_xaxes(title_text="Oilfield")
            bars_top_ten_gas.update_yaxes(title_text="Total Gas Produced (mmcfpd)")
            bars_top_ten_gas.update_traces(marker_color='#82a1b8', marker_line_color='#132847', marker_line_width=1.5, opacity=0.6)
            bars_top_ten_gas.update_layout(title_text='Top 15 Gas Producer Fields')
        
            bars_top_ten_gaswell = px.bar(oilwells, x='gas_cmpd', y='terminacion', labels={'Well':'Gas Production'}, orientation='h', color='gas_cmpd', color_continuous_scale='RdBu')
            bars_top_ten_gaswell.update_xaxes(title_text="Total Gas Produced [Cubic Meters per Day]")
            bars_top_ten_gaswell.update_yaxes(title_text="Well")
            bars_top_ten_gaswell.update_layout(title_text='Top 25 Gas Producer Wells', yaxis={'categoryorder':'total ascending'}, yaxis_tickangle=-40)
            bars_top_ten_gaswell.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', width=500)    
            bars_top_ten_gaswell.update_traces(texttemplate='%{x:.2s}', textposition='auto')
            bars_top_ten_gaswell.update_coloraxes(showscale=False)
            
            pie_gas = px.pie(oilfields, names='campo', values='gas_cmpd', color='campo', color_discrete_sequence=px.colors.sequential.RdBu, title='Accumulated Gas Production (Field)', width=500)
            pie_gas.update_traces(textposition='inside', textinfo='percent+label', textfont_size=7)
            pie_gas.update_layout(uniformtext_minsize=7, showlegend=False)
            
            st.plotly_chart(bars_top_ten_gas)
            bars_pie_gas = st.columns(2)
            bars_pie_gas[0].plotly_chart(pie_gas)
            bars_pie_gas[1].plotly_chart(bars_top_ten_gaswell)    
        
        if data_stats_selector == 'Water Production Statistics':
            #WATER#
            bars_top_ten_water = px.bar(waterfields, x='campo', y='agua_bpd', labels={'Well':'Water Production'}, height=400, width=1000)
            bars_top_ten_water.update_xaxes(title_text="Oilfield")
            bars_top_ten_water.update_yaxes(title_text="Total Water Produced (BPD)")
            bars_top_ten_water.update_traces(marker_color='#82a1b8', marker_line_color='#132847', marker_line_width=1.5, opacity=0.6)
            bars_top_ten_water.update_layout(title_text='Top 15 Water Producer fields')
            
            bars_top_ten_waterwell = px.bar(oilwells, x='agua_bpd', y='terminacion', labels={'Well':'Oil Production'}, orientation='h', color='agua_bpd', color_continuous_scale='RdBu')
            bars_top_ten_waterwell.update_xaxes(title_text="Well")
            bars_top_ten_waterwell.update_yaxes(title_text="Total Water Produced [bbls/d]")
            bars_top_ten_waterwell.update_layout(title_text='Top 25 Water Producer Wells', yaxis={'categoryorder':'total ascending'}, yaxis_tickangle=-40)
            bars_top_ten_waterwell.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', width=500)    
            bars_top_ten_waterwell.update_traces(texttemplate='%{x:.2s}', textposition='auto')
            bars_top_ten_waterwell.update_coloraxes(showscale=False)
            
            pie_water = px.pie(oilfields, names='campo', values='agua_bpd', color='campo', color_discrete_sequence=px.colors.sequential.RdBu, title='Accumulated Water Production (Field)', width=500)
            pie_water.update_traces(textposition='inside', textinfo='percent+label', textfont_size=7)
            pie_water.update_layout(uniformtext_minsize=7, showlegend=False)
            
            st.plotly_chart(bars_top_ten_water)
            bars_pie_water = st.columns(2)
            bars_pie_water[0].plotly_chart(pie_water)    
            bars_pie_water[1].plotly_chart(bars_top_ten_waterwell)
        
    ############################################################################################################################################################################################################
    with st.expander('GIS Maps and 3D Plots'):
        st.subheader('GIS Maps')
        GIS_map_selector = st.selectbox('choose a map to plot', ('None', 'Location', 'Sitio Grande Map', 'Production Lifespan', 'SG Wells MD',
                                                     'Last Production', 'Current Water Cut', 'Initial Production', 
                                                     'Acummulated Production', 'Acummulated Production (%)', 'Acummulated Production (%) - (2)', 'Yearly Production (MMBLS)', 
                                                     'Mud Loss', 'Water Injection', 'Water Injection - Zone A', 
                                                     'Water Injection - Zone B', 'Water Injection - Zone C', 'Water Injection - Zone D', 
                                                     'Thickness KM-A', 'Thickness KM-A (2)', 'Thickness KMA-KMB', 
                                                     'Thickness KMB-KMC', 'Thickness KMC-KMD', 'Thickness KMD-KS2', 
                                                     'Thickness KS2-KS3', 'Thickness KS3-KSF', 'Thickness KSF-KSMEN', 
                                                     'Salinity 75-76', 'Salinity 80', 'Salinity 84', 
                                                     'Salinity 90', 'Salinity 2004', 'Salinity 2021'))
        
        if GIS_map_selector == 'None':
            st.write(' ')
        if GIS_map_selector == 'Location':
            st.image('Maps\loc.png') 
        if GIS_map_selector == 'Sitio Grande Map':
            st.image('Maps\SG.png')
        if GIS_map_selector == 'Production Lifespan':
            st.image('Maps\lifespan.png')
        if GIS_map_selector == 'SG Wells MD':
            st.image('Maps\depth.png')
        if GIS_map_selector == 'Last Production':
            st.image('Maps\last prod.png')
        if GIS_map_selector == 'Current Water Cut':
            st.image('Maps\water cut.png')
        if GIS_map_selector == 'Initial Production':
            st.image('Maps\initial prod.png')
        if GIS_map_selector == 'Acummulated Production':
            st.image('Maps\cum.png')
        if GIS_map_selector == 'Acummulated Production (%)':
            st.image('Maps\cum percent.png')
        if GIS_map_selector == 'Acummulated Production (%) - (2)':
            st.image('Maps\cum percent 2.png')
        if GIS_map_selector == 'Acummulated Production (%) - (2)':
            st.image('Maps\cum percent 2.png')
        if GIS_map_selector == 'Yearly Production (MMBLS)':
            st.image('Maps\yearly.png')
        if GIS_map_selector == 'Mud Loss':
            st.image('Maps\mud loss.png')
        if GIS_map_selector == 'Water Injection':
            st.image('Maps\water in.png')
        if GIS_map_selector == 'Water Injection - Zone A':
            st.image('Maps\water in - A.png')
        if GIS_map_selector == 'Water Injection - Zone B':
            st.image('Maps\water in - B.png')
        if GIS_map_selector == 'Water Injection - Zone C':
            st.image('Maps\water in - C.png')
        if GIS_map_selector == 'Water Injection - Zone D':
            st.image('Maps\water in - D.png')  
        if GIS_map_selector == 'Thickness KM-A':
            st.image('Maps\kma_1.png')
        if GIS_map_selector == 'Thickness KM-A (2)':
            st.image('Maps\kma_2.png')
        if GIS_map_selector == 'Thickness KMA-KMB':
            st.image('Maps\kma-kmb.png')
        if GIS_map_selector == 'Thickness KMB-KMC':
            st.image('Maps\kmb-kmc.png')
        if GIS_map_selector == 'Thickness KMC-KMD':
            st.image('Maps\kmc-kmd.png')
        if GIS_map_selector == 'Thickness KMD-KS2':
            st.image('Maps\kmd-ks2.png')
        if GIS_map_selector == 'Thickness KS2-KS3':
            st.image('Maps\ks2-ks3.png')
        if GIS_map_selector == 'Thickness KS3-KSF':
            st.image('Maps\ks3-ksf.png')
        if GIS_map_selector == 'Thickness KSF-KSMEN':
            st.image('Maps\ksf-ksmen.png')
            
        st.subheader('3D Plots')
        
        formaciones = tops['formacion'].unique()
        filt_forms = st.selectbox('Select a formation', formaciones)
        top = tops[tops['formacion'] == filt_forms]
        
        x=tops['x']
        y=tops['y']
        z=tops['profundidad (m)']
        
        plt3D_select = st.selectbox('Type of plot', ('None', 'Formation Layer'))
        
        opacity_1 = st.slider('Opacity', 0.0, 1.0, (0.50),0.005)
        
        #well_tops = px.scatter_3d(top, x=x, y=y, z=z*-1, color=z*-1, color_continuous_scale='Viridis', 
        #                size=z, hover_name='terminacion', opacity=opacity_1)
        #well_tops.update_layout(width=1000, height=800)
        #well_tops.update_layout(title=f"{filt_forms} - Well X/Y/Z")
        #well_tops.update_layout(legend=dict(orientation="h",xanchor="center",yanchor="bottom",y=1.02,x=1))
        #well_tops.update_layout(paper_bgcolor="#F0F2F6", template="plotly_dark")
        #well_tops.update_scenes(camera_projection_type='orthographic')
        
        form_layer = go.Figure(data=[go.Mesh3d(x=x, y=y, z=z, opacity=opacity_1, intensity=z*-1, hoverinfo='all', 
                                               colorscale='Viridis', showlegend = True, name = f'{filt_forms}')])
        form_layer.update_layout(width=1000, height=800)
        form_layer.update_layout(title=f"{filt_forms} - {filt_campos}")
        form_layer.update_layout(legend=dict(orientation="h",xanchor="center",yanchor="bottom",y=1.02,x=1))
        form_layer.update_layout(paper_bgcolor="#F0F2F6", template="plotly_dark")
        form_layer.update_scenes(camera_projection_type='orthographic')
        
        if plt3D_select == 'None':
            st.write(' ')
        #if plt3D_select == 'Well Tops x/y/z':
        #    st.plotly_chart(well_tops)
        if plt3D_select == 'Formation Layer':
            st.plotly_chart(form_layer)
