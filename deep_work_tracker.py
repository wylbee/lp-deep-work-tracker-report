#%%
import streamlit as st 
import pandas as pd 
import numpy as np 
import altair as alt 
# %%
st.title("Deep Work Tracker")
#%%
raw = pd.read_excel("deep_work_tracker.xlsx")

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
heatmap_weekday = alt.Chart(heatmap_wrangled_filtered).mark_rect().encode(
    x= alt.X("weekday:O", title="Day of Week"),
    y= alt.Y("pd_week_number:O", title="Week #"),
    color= alt.Color('sum(minutes):Q',scale=alt.Scale(scheme="warmgreys"), legend=None),
    tooltip=[
        alt.Tooltip('monthdate(date):T', title='Date'),
        alt.Tooltip('sum(minutes):Q', title='Minutes')
    ]
).transform_filter(
    alt.FieldOneOfPredicate(field='weekday', oneOf=[1,2,3,4,5])
)

heatmap_weekend = alt.Chart(heatmap_wrangled_filtered).mark_rect().encode(
    x= alt.X("weekday:O", title=None),
    y= alt.Y("pd_week_number:O", axis=None),
    color= alt.Color('sum(minutes):Q',scale=alt.Scale(scheme="warmgreys"), legend=None),
    tooltip=[
        alt.Tooltip('monthdate(date):T', title='Date'),
        alt.Tooltip('sum(minutes):Q', title='Minutes')
    ]
).transform_filter(
    alt.FieldOneOfPredicate(field='weekday', oneOf=[6,7])
)

heatmap_weekly_goal = alt.Chart(heatmap_wrangled_filtered).transform_aggregate(
    total_minutes='sum(minutes)',
    groupby=['pd_week_number']
).mark_rect().encode(
    x=alt.X('year(date):O', axis = None),
    y=alt.Y("pd_week_number:O", axis= None),
    color= alt.condition(
        alt.datum.total_minutes > 1440,
        alt.value("steelblue"),
        alt.value("orange")
    ),
    tooltip=[
        alt.Tooltip('sum(minutes):Q'),
        alt.Tooltip('total_minutes:Q')
    ]
)

full_heatmap = alt.HConcatChart(hconcat=(heatmap_weekday, heatmap_weekend, heatmap_weekly_goal), title="Deep work minutes by weekday with goal tracker")


st.altair_chart(full_heatmap)