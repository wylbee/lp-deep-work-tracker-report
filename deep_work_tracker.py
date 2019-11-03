# %% codecell
import altair as alt
import numpy as np
import pandas as pd
# %% codecell
raw = pd.read_excel(r'C:\Users\brown\OneDrive\deep_work_tracker.xlsx')
raw.head()
# %% codecell
wrangled = raw.copy()
# %% codecell
alt.Chart(wrangled).mark_bar().encode(
    column='week_number',
    x='minutes',
    y='weekday:O',
    color=alt.Color('type', scale= alt.Scale(scheme='magma')),
    tooltip='minutes'
).properties(width=220, height = 220)
# %% codecell
alt.Chart(wrangled).mark_bar().encode(
    column='week_number',
    x='minutes',
    y='weekday:O',
    color=alt.Color('type', scale= alt.Scale(scheme='magma')),
    tooltip='minutes'
).properties(width=220, height = 220)
# %% codecell
from vega_datasets import data
source = data.barley()
source.head()
# %% codecell
alt.Chart(source).mark_bar().encode(
    column='year',
    x='yield',
    y='variety',
    color='site'
).properties(width=220)
# %% codecell
