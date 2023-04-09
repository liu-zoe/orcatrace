## Project Name: Orca movement
### Program Name: app.py
### Purpose: To make a dash board for southern resident killer whales movement
##### Date Created: Apr 1st 2023
#%%
import os
from os.path import join as pjoin
from multiprocessing import Process
import signal

import datetime
from datetime import date
from datetime import datetime as dt 
from time import strptime
from time import sleep
import calendar
import pytz
from pytz import timezone

import pandas as pd
pd.options.mode.chained_assignment = None #suppress chained assignment 

import numpy as np
import streamlit as st

import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.express as px

import transbigdata as tbd
import keplergl
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl

# Define path to data 
base_path=os.path.abspath("")
srkw_sattellite_path=pjoin(base_path, 'data')
mapbox_access_token = os.environ.get('MAPBOX_TOKEN')
#mapbox_access_token = open(pjoin(base_path,"mapbox_token.txt")).read()

# -- Set page config
apptitle = 'SRKW Movement'
iconfile=pjoin(base_path, "assets", "favicon.ico")
st.set_page_config(page_title=apptitle, page_icon=iconfile)
# Load in SRKW Satellite Tagging data
# Functions gmt2pst: convert GMT time to Pacific Time
def gmt2pst(yr,mon,day,h,m,s):
    tz=pytz.timezone('GMT')
    _date1=dt(yr, mon, day,h,m,s, tzinfo=tz)
    _date2=_date1.astimezone(timezone('US/Pacific'))
    return(_date2)
# Function orcaday: create number of days of orca movement from the earliest record
def orcaday(dat):
    day0=min(dat['date'])
    dat['day_move']=dat['date'].apply(lambda x: x-day0)
# Function geogen: create longitude and latitide 
def geogen(dat):
    import numpy as np
    dat['lon']=np.where(dat['lon_p']>-120, dat['lon_a'],dat['lon_p'])
    dat['lat']=np.where(dat['lon_p']>-120, dat['lat_a'],dat['lat_p'])

satellite_fname="SRKW occurrence coastal - SRKW occurrence coastal Data.csv"
satellite=pd.read_csv(pjoin(srkw_sattellite_path, satellite_fname))
satellite=satellite.rename(columns={'Lat P':'lat_p', 'Lon P':'lon_p', 'Lat A':'lat_a','Lon A':'lon_a'})
satellite=satellite[['Animal', 'lat_p', 'lon_p', 'lat_a',
       'lon_a', 'Dur', 'Sex', 'Popid', 
       'Month', 'Day', 'Year', 'Hour', 'Minute', 'Second']]
satellite['Popid']=satellite['Popid'].apply(lambda x: x.replace(' ',''))
satellite['datetime_pst']=satellite.apply(lambda x: gmt2pst(x.Year, x.Month, x.Day, x.Hour, x.Minute, x.Second), axis=1)
satellite=satellite.drop(columns=['Year','Month','Day','Hour','Minute','Second'])
satellite['date']=satellite.apply(lambda x: x.datetime_pst.date(), axis=1)
satellite['date_str']=satellite.apply(lambda x: str(x.datetime_pst.date()), axis=1)
satellite['time']=satellite.apply(lambda x: x.datetime_pst.time(), axis=1)
satellite['year']=satellite.apply(lambda x: x.date.year, axis=1)
satellite['month']=satellite.apply(lambda x: x.date.month, axis=1)
satellite['day']=satellite.apply(lambda x: x.date.day, axis=1)
satellite['hour']=satellite.apply(lambda x: x.time.hour, axis=1)
satellite['minute']=satellite.apply(lambda x: x.time.minute, axis=1)
satellite['second']=satellite.apply(lambda x: x.time.second, axis=1)
satellite['time_str']=satellite.apply(lambda x: str(x.datetime_pst.time().strftime("%I:%M %p")), axis=1)
satellite['datetime_str']=satellite.apply(lambda x: x.time_str+' '+x.date_str, axis=1)
satellite['day_of_year']=satellite['date'].apply(lambda x: pd.Period(x, freq='D').day_of_year)
satellite_j26=satellite[satellite.Popid=='J26']
satellite_j27=satellite[satellite.Popid=='J27']
satellite_k25=satellite[satellite.Popid=='K25']
satellite_k33=satellite[satellite.Popid=='K33']
satellite_l84=satellite[satellite.Popid=='L84']
satellite_l87=satellite[satellite.Popid=='L87']
satellite_l88=satellite[satellite.Popid=='L88']
satellite_l95=satellite[satellite.Popid=='L95']
# make an initial list of timestamps with j26
def make_slider_mark(indat, skip=0): 
    timelist=list(indat['datetime_str'])
    mark_index=list(range(len(timelist)))
    # mark_index=[]
    # timelist=[]
    # i=indat.shape[0]-1
    # while (i>=0):
    #     mark_index.append(i)
    #     timelist.append()
    #     i-=(skip+1)
    # mark_index.reverse()
    # timelist.reverse()
    return(mark_index, timelist)
mark_index, timelist=make_slider_mark(satellite_j26)
#%%
def orca_picker(orca):
    #Pick orca
    if orca=="J26":
        orca_dat=satellite_j26
        zoom_val=7
        name="Mike"
        age=min(orca_dat['year'])-1991
    if orca=="J27":
        orca_dat=satellite_j27
        zoom_val=6        
        name="Blackberry"
        age=min(orca_dat['year'])-1991
    if orca=="K25":
        orca_dat=satellite_k25
        zoom_val=4
        name="Scoter"
        age=min(orca_dat['year'])-1991
    if orca=="K33":
        orca_dat=satellite_k33
        zoom_val=4
        name="Tika"
        age=min(orca_dat['year'])-2001
    if orca=="L84":
        orca_dat=satellite_l84
        zoom_val=4
        name="Nyssa"
        age=min(orca_dat['year'])-1990
    if orca=="L87":
        orca_dat=satellite_l87
        zoom_val=6
        name="Onyx"
        age=min(orca_dat['year'])-1992
    if orca=="L88":
        orca_dat=satellite_l88
        zoom_val=5
        name="Wave Walker"
        age=min(orca_dat['year'])-1993
    if orca=="L95":
        orca_dat=satellite_l95
        zoom_val=5
        name="Nigel"
        age=min(orca_dat['year'])-1996
    orcaday(orca_dat)
    geogen(orca_dat)
    orca_dat=orca_dat.sort_values(by=['datetime_pst'])
    lon_avg=orca_dat['lon'].mean()
    lat_avg=orca_dat['lat'].mean()
    #Define orca tag
    orca_tag=" ".join([orca, name, "("+str(age)+"yr )"])
    #create index for slider
    mark_index, timelist=make_slider_mark(orca_dat)
    return (orca_dat, orca_tag, zoom_val, lon_avg, lat_avg, mark_index, timelist)
#%%
def update_orca_trace(orca_dat, 
lon_avg, lat_avg, zoom_val,
index,
):
    #Pick time
    orca_dat=orca_dat.iloc[index:index+2, :]
    target=orca_dat.iloc[1, :]
    #Make plot
    fig_orcamove = go.Figure()

    fig_orcamove.add_trace(
        go.Scattermapbox(
            lat=orca_dat['lat'],
            lon=orca_dat['lon'],
            mode='lines',
            marker=go.scattermapbox.Marker(
                color="#016fb9",
                #color=orca_dat['day_move'],
                #colorscale='Blues',
                size=9,
                opacity=0.75,
            ),        
            text=orca_dat['datetime_pst'],
            hoverinfo='text'
        ))
    fig_orcamove.add_trace(
        go.Scattermapbox(
            lat=[target['lat']],
            lon=[target['lon']],
            mode='markers',
            name="",
            marker=go.scattermapbox.Marker(
                color="#016fb9",
                #color=orca_dat['day_move'],
                #colorscale='Blues',
                size=10,
                opacity=0.75,
            ),   
            text=[target['datetime_pst']],
            hoverinfo='text'     
        ))
    fig_orcamove.update_layout(
        autosize=True,
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=lat_avg,
                lon=lon_avg
            ),
            zoom=zoom_val,
            style='dark'
        ),
    )    
    return fig_orcamove
# orca_dat, orca_tag, zoom_val, lon_avg, lat_avg, mark_index, timelist=orca_picker("J26")
# fig=update_orca_trace(orca_dat, 
# lon_avg, lat_avg, zoom_val,
# 0)
# fig.show()
#%%
st.header('Southern Resident Killer Whales Tracing')
#slider_rack=st.empty()
status_text = st.empty()
map_frame = st.empty()

####-----SIDE BAR-------#
# Orca info
st.sidebar.markdown("## Select Orca")
selected_orca = st.sidebar.selectbox('',
                                     ['J26', 'J27', 'K25', 'K33', 'L84','L87','L88','L95'])
orca_dat, orca_tag, zoom_val, lon_avg, lat_avg, mark_index, timelist=orca_picker(selected_orca)

st.sidebar.markdown(orca_tag)

# interval
st.sidebar.markdown("## Select interval time (sec)")
int_sec=st.sidebar.selectbox('', [0.1, 0.5, 1, 2, 3])

#Play/Pause buttons
play=st.sidebar.button('Play')
# pause=st.sidebar.button('Pause')
# stop=st.sidebar.button('Stop')
refresh=st.sidebar.button('Refresh')
# if 'play_count' not in st.session_state:
#     st.session_state['play_count'] = 0
# if 'pause_count' not in st.session_state:
#     st.session_state['pause_count'] = 0
# play_c = st.session_state['play_count']
# pause_c=st.session_state['pause_count']
# st.sidebar.markdown(f"Play count: {play_c}")
# st.sidebar.markdown(f"Puase count: {pause_c}")

# if play:
#     play_c+=1

# if pause:
#     pause_c+1
####-----MAIN FRAME-------#
if play:
    # slider_rack.slider(" ", min_value=0, max_value=len(timelist)-2, key=999)
    for i in mark_index[:-1]:
    #     slider_rack.slider(
    #         " ",
    #         max_value=len(timelist)-2,
    #         value=i,
    #         format=timelist[i],
    #         key=i
    #     )
        timestamp=timelist[i]
        status_text.text(f"{timestamp}")
        fig=update_orca_trace(orca_dat, lon_avg, lat_avg, zoom_val, i)
        with map_frame:
            st.plotly_chart(fig, use_container_width=True)
        if i==0:
            sleep(2)
        sleep(int_sec)
map=tbd.visualization_trip(orca_dat, col=['lon', 'lat', 'Animal', 'datetime_pst'],)
keplergl_static(map)
play_timestamp=False
pause_timestamp=False