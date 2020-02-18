#%%
import streamlit as st 
import pandas as pd 
import numpy as np 
import altair as alt 

#%%
raw = pd.read_excel("deep_work_tracker.xlsx")

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

growth_goal_minutes = 9 * 60
bacon_goal_minutes = 5 * 3 * 60

growth_types = ['Professional Development', 'Learning Project', 'Agile Data Science']
bacon_types = ['Sprint']

# %%
heatmap_weekday_growth = alt.Chart(heatmap_wrangled_filtered).mark_rect().encode(
    x= alt.X("weekday:O", title="Day of Week"),
    y= alt.Y("pd_week_number:O", title="Week #"),
    color= alt.Color('sum(minutes):Q',scale=alt.Scale(scheme="warmgreys"), legend=None),
    tooltip=[
        alt.Tooltip('monthdate(date):T', title='Date'),
        alt.Tooltip('sum(minutes):Q', title='Minutes')
    ]
).transform_filter(
    alt.FieldOneOfPredicate(field='weekday', oneOf=[1,2,3,4,5]) 
).transform_filter(
    alt.FieldOneOfPredicate(field='type', oneOf = growth_types)
)

heatmap_weekend_growth = alt.Chart(heatmap_wrangled_filtered).mark_rect().encode(
    x= alt.X("weekday:O", title=None),
    y= alt.Y("pd_week_number:O", axis=None),
    color= alt.Color('sum(minutes):Q',scale=alt.Scale(scheme="warmgreys"), legend=None),
    tooltip=[
        alt.Tooltip('monthdate(date):T', title='Date'),
        alt.Tooltip('sum(minutes):Q', title='Minutes')
    ]
).transform_filter(
    alt.FieldOneOfPredicate(field='weekday', oneOf=[6,7])
).transform_filter(
    alt.FieldOneOfPredicate(field='type', oneOf = growth_types)
)

heatmap_weekly_goal_growth = alt.Chart(heatmap_wrangled_filtered).transform_filter(
    alt.FieldOneOfPredicate(field='type', oneOf = growth_types)
).transform_aggregate(
    total_minutes='sum(minutes)',
    groupby=['pd_week_number']
).mark_rect().encode(
    x=alt.X('year(date):O', axis = alt.Axis(ticks= False, labels = False, title='Goal Met?')),
    y=alt.Y("pd_week_number:O", axis= None),
    color= alt.condition(
        alt.datum.total_minutes > growth_goal_minutes,
        alt.value("steelblue"),
        alt.value("orange")
    ),
    tooltip=[
        alt.Tooltip('total_minutes:Q', title = "Total Minutes")
    ]
)

stacked_bar_growth = alt.Chart(heatmap_wrangled_filtered).mark_bar().encode(
    y=alt.Y("pd_week_number:O", axis=None),
    x="sum(minutes):Q",
    color="type",
    tooltip="sum(minutes):Q"
).transform_filter(
    alt.FieldOneOfPredicate(field='type', oneOf = growth_types)
)

full_heatmap_growth = alt.HConcatChart(hconcat=(heatmap_weekday_growth, heatmap_weekend_growth, heatmap_weekly_goal_growth, stacked_bar_growth), title="Deep work minutes towards growth goal by week")

# %%
heatmap_weekday_bacon = alt.Chart(heatmap_wrangled_filtered).mark_rect().encode(
    x= alt.X("weekday:O", title="Day of Week"),
    y= alt.Y("pd_week_number:O", title="Week #"),
    color= alt.Color('sum(minutes):Q',scale=alt.Scale(scheme="warmgreys"), legend=None),
    tooltip=[
        alt.Tooltip('monthdate(date):T', title='Date'),
        alt.Tooltip('sum(minutes):Q', title='Minutes')
    ]
).transform_filter(
    alt.FieldOneOfPredicate(field='weekday', oneOf=[1,2,3,4,5]) 
).transform_filter(
    alt.FieldOneOfPredicate(field='type', oneOf = bacon_types)
)

heatmap_weekend_bacon = alt.Chart(heatmap_wrangled_filtered).mark_rect().encode(
    x= alt.X("weekday:O", title=None),
    y= alt.Y("pd_week_number:O", axis=None),
    color= alt.Color('sum(minutes):Q',scale=alt.Scale(scheme="warmgreys"), legend=None),
    tooltip=[
        alt.Tooltip('monthdate(date):T', title='Date'),
        alt.Tooltip('sum(minutes):Q', title='Minutes')
    ]
).transform_filter(
    alt.FieldOneOfPredicate(field='weekday', oneOf=[6,7])
).transform_filter(
    alt.FieldOneOfPredicate(field='type', oneOf = bacon_types)
)

heatmap_weekly_goal_bacon = alt.Chart(heatmap_wrangled_filtered).transform_filter(
    alt.FieldOneOfPredicate(field='type', oneOf = bacon_types)
).transform_aggregate(
    total_minutes='sum(minutes)',
    groupby=['pd_week_number']
).mark_rect().encode(
    x=alt.X('year(date):O', axis = alt.Axis(ticks= False, labels = False, title='Goal Met?')),
    y=alt.Y("pd_week_number:O", axis = None),
    color= alt.condition(
        alt.datum.total_minutes > bacon_goal_minutes,
        alt.value("steelblue"),
        alt.value("orange")
    ),
    tooltip=[
        alt.Tooltip('total_minutes:Q', title = "Total Minutes")
    ]
)

stacked_bar_bacon = alt.Chart(heatmap_wrangled_filtered).mark_bar().encode(
    y=alt.Y("pd_week_number:O", axis=None),
    x="sum(minutes):Q",
    color= "type",
    tooltip="sum(minutes):Q"
).transform_filter(
    alt.FieldOneOfPredicate(field='type', oneOf = bacon_types)
)

full_heatmap_bacon = alt.HConcatChart(hconcat=(heatmap_weekday_bacon, heatmap_weekend_bacon, heatmap_weekly_goal_bacon, stacked_bar_bacon), title="Deep work minutes towards professional goal by week")

# %%

heatmap_weekly_goal_growth_with_axis = alt.Chart(heatmap_wrangled_filtered).transform_filter(
    alt.FieldOneOfPredicate(field='type', oneOf = growth_types)
).transform_aggregate(
    total_minutes='sum(minutes)',
    groupby=['pd_week_number']
).mark_rect().encode(
    x=alt.X('year(date):O', axis = alt.Axis(ticks= False, labels = False, title='Goal Met?')),
    y=alt.Y("pd_week_number:O", title='Week #'),
    color= alt.condition(
        alt.datum.total_minutes > growth_goal_minutes,
        alt.value("steelblue"),
        alt.value("orange")
    ),
    tooltip=[
        alt.Tooltip('total_minutes:Q', title = "Total Minutes")
    ]
)

consolidated_goals = alt.HConcatChart(hconcat=(heatmap_weekly_goal_growth_with_axis,heatmap_weekly_goal_bacon), title= 'Growth & professional goals')
# %%
st.title("Deep Work Tracker")
st.subheader('Overview')
st.markdown(f"""
The purpose of this tool is to track the leading indicator of Deep Work minutes against selected goals and allow for exploration of where that time is being spent.

A quick reference for Newport's Deep Work can be found [here](https://doist.com/blog/deep-work/). As defined, Deep Work is:
>“Professional activity performed in a state of distraction-free concentration that push your cognitive capabilities to their limit. These efforts create new value, improve your skill, and are hard to replicate.”

My weekly goals are as follows:
* Growth - {growth_goal_minutes/60} hours per week ({growth_goal_minutes} minutes); spent developing skills
* Professional - {bacon_goal_minutes/60} hours per week ({bacon_goal_minutes} minutes); spent on executing the day job

Current progress is tallied in summary form here, then detailed in the relevant sub-sections below.
""")

st.altair_chart(consolidated_goals)

st.subheader('Growth')
st.altair_chart(full_heatmap_growth)
st.subheader('Professional')
st.altair_chart(full_heatmap_bacon)