# %% codecell
import pandas as pd
import altair as alt
import numpy as np

# %% codecell
raw = pd.read_excel(r'C:\Users\brown\OneDrive\deep_work_tracker.xlsx')

# %% codecell
wrangled = raw.copy()
#wrangled.assign

# %% codecell
upper = alt.Chart(wrangled).mark_rect().encode(
    x = 'week_number:O',
    y = 'weekday:O',
    color = 'minutes:Q'
)

lower = alt.Chart(wrangled).mark_bar().encode(
    x = 'sum(minutes):Q',
    y = 'type:N'
)
 
alt.vconcat(upper,lower)

# %% codecell
alt.Chart(wrangled).mark_rect().encode(
    x = 'week_number:O',
    y = 'weekday:O',
    color = 'minutes:Q'
).facet(
    column = 'type:N'
)
