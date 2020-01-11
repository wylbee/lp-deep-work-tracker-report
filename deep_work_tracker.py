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
#date_range = 

heatmap_wrangled = raw.copy() 

# %%

heatmap = alt.Chart(heatmap_wrangled).mark_rect().encode(
    x="week_number:O",
    y="weekday:O",
    color="minutes:Q",
    tooltip="minutes:Q"
)

st.altair_chart(heatmap, width=0)