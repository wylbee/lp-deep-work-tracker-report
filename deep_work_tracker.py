#%%
import streamlit as st 
import pandas as pd 
import numpy as np 
import altair as alt 
# %%
st.title("Deep Work Tracker")
#%%
raw = pd.read_excel("/home/brown5628/projects/lp-deep-work-tracker-report/deep_work_tracker.xlsx")

# %%
st.subheader("Graph")

# %% 
heatmap_wrangled = raw.copy()
heatmap_wrangled = (
    heatmap_wrangled
    .assign(year = pd.DatetimeIndex(heatmap_wrangled['date']).year)
    #.assign(year_week_number = pd.DatetimeIndex(heatmap_wrangled['date']).year + heatmap_wrangled['week_number'])
    .assign(pd_week_number = heatmap_wrangled['date'].dt.strftime('%W'))
)
#https://strftime.org/
#https://stackoverflow.com/questions/31181295/converting-a-pandas-date-to-week-number
year_filter_value = 2020
heatmap_wrangled_filtered = (
    heatmap_wrangled.copy()
    .query(f'year=={year_filter_value}')
)

weekly_dw_goal = 100
# %%
base_master_heatmap = alt.Chart(heatmap_wrangled_filtered).transform_joinaggregate(
    sum_minutes = 'sum(minutes):Q',
    groupby=["pd_week_number"]
).transform_calculate(
    color = 'datum.sum_minutes < 1200 ? "orange" : "blue"'
)

master_heatmap = base_master_heatmap.mark_rect().encode(
    alt.X('pd_week_number:O', title='week'),
    alt.Y('month(date):O', title='month'),
    color= alt.Color('color:N', scale=None),
    tooltip = "sum(minutes):Q"
).properties(
    title='Deep Work Minutes by Week'
)

# %%

alt_heat = alt.Chart(heatmap_wrangled_filtered, title="Another Heatmap").mark_rect().encode(
    x='date(date):O',
    y='month(date):O',
    color = alt.Color('sum(minutes):Q',scale=alt.Scale(scheme="inferno")),
    tooltip=[
        alt.Tooltip('monthdate(date):T', title='Date'),
        alt.Tooltip('sum(minutes):Q', title='Minutes')
    ]
)
# %%

heatmap = alt.Chart(heatmap_wrangled_filtered).mark_rect().encode(
    x="pd_week_number:O",
    y="weekday:O",
    color="minutes:Q",
    tooltip="minutes:Q"
)

stacked_bar = alt.Chart(heatmap_wrangled_filtered).mark_bar().encode(
    x="pd_week_number:O",
    y="sum(minutes):Q",
    color="type",
    tooltip="sum(minutes):Q"
)

# %%
st.altair_chart(master_heatmap, width=0)

st.altair_chart(alt_heat)

st.altair_chart(alt.vconcat(heatmap,stacked_bar), width=0)

# %%
