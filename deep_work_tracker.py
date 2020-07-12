# %%
import streamlit as st
import pandas as pd
import altair as alt
import psycopg2
import os

# %%
growth_goal_minutes = 2 * 3 * 60
bacon_goal_minutes = 5 * 3 * 60

# %%
db_host = os.getenv("SWA_DB_HOST")
db_port = os.getenv("SWA_DB_PORT")
db_db = os.getenv("SWA_DB_DB")
db_user = os.getenv("SWA_DB_USER")
db_pass = os.getenv("SWA_DB_PASS")

# %%
conn = psycopg2.connect(
    host=db_host, port=db_port, database=db_db, user=db_user, password=db_pass
)

cur = conn.cursor()

# %%


def create_df_from_query(sql_query, database=conn):
    df = pd.read_sql_query(sql_query, database)
    return df


# %%

raw = create_df_from_query(
    """
    select
         activity_date + '00:00:01'::time as date,
         activity_week_number as week_number,
         activity_weekday as weekday,
         activity_type as type,
         activity_subtype as subtype,
         activity_minutes as minutes

    from mart_quantified_self.fct_deep_work_tracker

"""
)

# %%
cur.close()
conn.close()

# %%
heatmap_wrangled = raw.copy()
#heatmap_wrangled["date"] = pd.to_datetime(
#    heatmap_wrangled["date"], #infer_datetime_format=True, 
#    utc=False
#)
heatmap_wrangled = (
    heatmap_wrangled.assign(year=pd.DatetimeIndex(heatmap_wrangled["date"]).year)
    .assign(pd_week_number=heatmap_wrangled["date"].dt.strftime("%W"))
    .assign(growth_goal_minutes=growth_goal_minutes)
    .assign(bacon_goal_minutes=bacon_goal_minutes)
)
# https://strftime.org/
# https://stackoverflow.com/questions/31181295/converting-a-pandas-date-to-week-number
year_filter_value = 2020

heatmap_wrangled_filtered = heatmap_wrangled.copy().query(f"year=={year_filter_value}")

heatmap_wrangled_filtered_grouped = (
    heatmap_wrangled_filtered.copy()
    .groupby(
        [
            "date",
            "week_number",
            "weekday",
            "type",
            "subtype",
            "year",
            "pd_week_number",
            "growth_goal_minutes",
            "bacon_goal_minutes",
        ]
    )
    .agg({"minutes": "sum"})
    .reset_index()
)


growth_types = ["Professional Development", "Learning Project", "Agile Data Science"]
bacon_types = ["Sprint", "Slack"]

filtered_subtypes = (
    heatmap_wrangled_filtered_grouped.copy()
    .query("subtype != 'undefined'")["subtype"]
    .tolist()
)

# %%
heatmap_weekday_growth = (
    alt.Chart(heatmap_wrangled_filtered_grouped)
    .mark_rect()
    .encode(
        x=alt.X("weekday:O", title="Day of Week"),
        y=alt.Y("pd_week_number:O", title="Week #"),
        color=alt.Color(
            "sum(minutes):Q", scale=alt.Scale(scheme="warmgreys"), legend=None
        ),
        tooltip=[
            alt.Tooltip("monthdate(date):T", title="Date"),
            alt.Tooltip("sum(minutes):Q", title="Minutes"),
        ]
        # ).transform_filter(
        #    alt.FieldOneOfPredicate(field='weekday', oneOf=[1,2,3,4,5])
    )
    .transform_filter(alt.FieldOneOfPredicate(field="type", oneOf=growth_types))
)

# heatmap_weekend_growth = alt.Chart(heatmap_wrangled_filtered_grouped).mark_rect().encode(
#    x= alt.X("weekday:O", title=None),
#    y= alt.Y("pd_week_number:O", axis=None),
#    color= alt.Color('sum(minutes):Q',scale=alt.Scale(scheme="warmgreys"), legend=None),
#    tooltip=[
#        alt.Tooltip('monthdate(date):T', title='Date'),
#        alt.Tooltip('sum(minutes):Q', title='Minutes')
#    ]
# ).transform_filter(
#    alt.FieldOneOfPredicate(field='weekday', oneOf=[6,7])
# ).transform_filter(
#    alt.FieldOneOfPredicate(field='type', oneOf = growth_types)
# )

heatmap_weekly_goal_growth = (
    alt.Chart(heatmap_wrangled_filtered_grouped)
    .transform_filter(alt.FieldOneOfPredicate(field="type", oneOf=growth_types))
    .transform_aggregate(total_minutes="sum(minutes)", groupby=["pd_week_number"])
    .mark_rect()
    .encode(
        x=alt.X(
            "year(date):O", axis=alt.Axis(ticks=False, labels=False, title="Goal Met?")
        ),
        y=alt.Y("pd_week_number:O", axis=None),
        color=alt.condition(
            alt.datum.total_minutes >= growth_goal_minutes,
            alt.value("steelblue"),
            alt.value("orange"),
        ),
        tooltip=[alt.Tooltip("total_minutes:Q", title="Total Minutes")],
    )
)

stacked_bar_growth = (
    alt.Chart(heatmap_wrangled_filtered_grouped)
    .mark_bar()
    .encode(
        y=alt.Y("pd_week_number:O", axis=None),
        x=alt.X("sum(minutes):Q", title="Total minutes with mean and goal"),
        color=alt.Color("type:N", scale=alt.Scale(scheme="pastel1")),
        tooltip="sum(minutes):Q",
    )
    .transform_filter(alt.FieldOneOfPredicate(field="type", oneOf=growth_types))
)

avg_line_growth = (
    alt.Chart(heatmap_wrangled_filtered_grouped)
    .transform_filter(alt.FieldOneOfPredicate(field="type", oneOf=growth_types))
    .transform_aggregate(total_minutes="sum(minutes)", groupby=["pd_week_number"])
    .mark_rule(color="purple", opacity=0.3)
    .encode(x="mean(total_minutes):Q", tooltip=alt.Tooltip("mean(total_minutes):Q"))
)

goal_line_growth = (
    alt.Chart(heatmap_wrangled_filtered_grouped)
    .mark_rule(color="steelblue", opacity=0.3)
    .encode(x="growth_goal_minutes:Q")
)


full_heatmap_growth = alt.HConcatChart(
    hconcat=(
        heatmap_weekday_growth,
        heatmap_weekly_goal_growth,
        (stacked_bar_growth + avg_line_growth + goal_line_growth),
    ),
    title="Deep work minutes towards growth goal by week",
)


# %%

cumulative_sum_subtype_growth = (
    alt.Chart(heatmap_wrangled_filtered_grouped)
    .transform_filter(alt.FieldOneOfPredicate(field="subtype", oneOf=filtered_subtypes))
    .transform_filter(alt.FieldOneOfPredicate(field="type", oneOf=growth_types))
    .mark_line(opacity=0.5)
    .encode(
        x="monthdate(date):T", y="cumulative_minutes:Q", color="subtype:N", row="type:N"
    )
    .transform_window(
        cumulative_minutes="sum(minutes)", frame=[None, 0], groupby=["subtype"]
    )
)

# %%
heatmap_weekday_bacon = (
    alt.Chart(heatmap_wrangled_filtered_grouped)
    .mark_rect()
    .encode(
        x=alt.X("weekday:O", title="Day of Week"),
        y=alt.Y("pd_week_number:O", title="Week #"),
        color=alt.Color(
            "sum(minutes):Q", scale=alt.Scale(scheme="warmgreys"), legend=None
        ),
        tooltip=[
            alt.Tooltip("monthdate(date):T", title="Date"),
            alt.Tooltip("sum(minutes):Q", title="Minutes"),
        ]
        # ).transform_filter(
        #    alt.FieldOneOfPredicate(field='weekday', oneOf=[1,2,3,4,5])
    )
    .transform_filter(alt.FieldOneOfPredicate(field="type", oneOf=bacon_types))
)

# heatmap_weekend_bacon = alt.Chart(heatmap_wrangled_filtered_grouped).mark_rect().encode(
#    x= alt.X("weekday:O", title=None),
#    y= alt.Y("pd_week_number:O", axis=None),
#    color= alt.Color('sum(minutes):Q',scale=alt.Scale(scheme="warmgreys"), legend=None),
#    tooltip=[
#        alt.Tooltip('monthdate(date):T', title='Date'),
#        alt.Tooltip('sum(minutes):Q', title='Minutes')
#    ]
# ).transform_filter(
#    alt.FieldOneOfPredicate(field='weekday', oneOf=[6,7])
# ).transform_filter(
#    alt.FieldOneOfPredicate(field='type', oneOf = bacon_types)
# )

heatmap_weekly_goal_bacon = (
    alt.Chart(heatmap_wrangled_filtered_grouped)
    .transform_filter(alt.FieldOneOfPredicate(field="type", oneOf=bacon_types))
    .transform_aggregate(total_minutes="sum(minutes)", groupby=["pd_week_number"])
    .mark_rect()
    .encode(
        x=alt.X(
            "year(date):O", axis=alt.Axis(ticks=False, labels=False, title="Goal Met?")
        ),
        y=alt.Y("pd_week_number:O", axis=None),
        color=alt.condition(
            alt.datum.total_minutes >= bacon_goal_minutes,
            alt.value("steelblue"),
            alt.value("orange"),
        ),
        tooltip=[alt.Tooltip("total_minutes:Q", title="Total Minutes")],
    )
)

stacked_bar_bacon = (
    alt.Chart(heatmap_wrangled_filtered_grouped)
    .mark_bar()
    .encode(
        y=alt.Y("pd_week_number:O", axis=None),
        x=alt.X("sum(minutes):Q", title="Total minutes with mean and goal"),
        color=alt.Color("type:N", scale=alt.Scale(scheme="pastel2")),
        tooltip=alt.Tooltip("sum(minutes):Q", title="Total Minutes"),
    )
    .transform_filter(alt.FieldOneOfPredicate(field="type", oneOf=bacon_types))
)

avg_line_bacon = (
    alt.Chart(heatmap_wrangled_filtered_grouped)
    .transform_filter(alt.FieldOneOfPredicate(field="type", oneOf=bacon_types))
    .transform_aggregate(total_minutes="sum(minutes)", groupby=["pd_week_number"])
    .mark_rule(color="purple", opacity=0.3)
    .encode(x="mean(total_minutes):Q", tooltip=alt.Tooltip("mean(total_minutes):Q"))
)

goal_line_bacon = (
    alt.Chart(heatmap_wrangled_filtered_grouped)
    .mark_rule(color="steelblue", opacity=0.3)
    .encode(x="bacon_goal_minutes:Q")
)

full_heatmap_bacon = alt.HConcatChart(
    hconcat=(
        heatmap_weekday_bacon,
        heatmap_weekly_goal_bacon,
        (stacked_bar_bacon + avg_line_bacon + goal_line_bacon),
    ),
    title="Deep work minutes towards professional goal by week",
)

# %%
cumulative_sum_subtype_bacon = (
    alt.Chart(heatmap_wrangled_filtered_grouped)
    .transform_filter(alt.FieldOneOfPredicate(field="subtype", oneOf=filtered_subtypes))
    .transform_filter(alt.FieldOneOfPredicate(field="type", oneOf=bacon_types))
    .mark_line(opacity=0.5)
    .encode(
        x="monthdate(date):T", y="cumulative_minutes:Q", color="subtype:N", row="type:N"
    )
    .transform_window(
        cumulative_minutes="sum(minutes)", frame=[None, 0], groupby=["subtype"]
    )
)

# %%

heatmap_weekly_goal_growth_with_axis = (
    alt.Chart(heatmap_wrangled_filtered_grouped)
    .transform_filter(alt.FieldOneOfPredicate(field="type", oneOf=growth_types))
    .transform_aggregate(total_minutes="sum(minutes)", groupby=["pd_week_number"])
    .mark_rect()
    .encode(
        x=alt.X(
            "year(date):O", axis=alt.Axis(ticks=False, labels=False, title="Goal Met?")
        ),
        y=alt.Y("pd_week_number:O", title="Week #"),
        color=alt.condition(
            alt.datum.total_minutes > growth_goal_minutes,
            alt.value("steelblue"),
            alt.value("orange"),
        ),
        tooltip=[alt.Tooltip("total_minutes:Q", title="Total Minutes")],
    )
)

consolidated_goals = alt.HConcatChart(
    hconcat=(heatmap_weekly_goal_growth_with_axis, heatmap_weekly_goal_bacon),
    title="Growth & professional goals",
)
# %%
st.title("Deep Work Tracker")
st.subheader("Overview")
st.markdown(
    f"""
The purpose of this tool is to track the leading indicator of Deep Work minutes against selected goals and allow for exploration of where that time is being spent.

A quick reference for Newport's Deep Work can be found [here](https://doist.com/blog/deep-work/). As defined, Deep Work is:
>“Professional activity performed in a state of distraction-free concentration that push your cognitive capabilities to their limit. These efforts create new value, improve your skill, and are hard to replicate.”

My weekly goals are as follows:
* Growth - {growth_goal_minutes/60} hours per week ({growth_goal_minutes} minutes); spent developing skills
* Professional - {bacon_goal_minutes/60} hours per week ({bacon_goal_minutes} minutes); spent on executing the day job

Current progress is tallied in summary form here, then detailed in the relevant sub-sections below.
"""
)

st.altair_chart(consolidated_goals)

st.subheader("Growth")
st.altair_chart(full_heatmap_growth)
# st.altair_chart(cumulative_sum_subtype_growth)
st.subheader("Professional")
st.altair_chart(full_heatmap_bacon)
# st.altair_chart(cumulative_sum_subtype_bacon)


# st.write(heatmap_wrangled_filtered_grouped)
