import plotly.express as px

import plotly.graph_objects as go

import pandas as pd


df = px.data.gapminder().query("year == 2007")
df = pd.read_csv("location.csv")
df.head()

fig = go.Figure()

fig.add_trace(go.Scattergeo(
    lat=df['Lat'],
    lon=df['Lon'],
    text=df['Country'],
    geo='geo',
    marker=dict(
        size=df['Total']*8,
        line_width=0,
        color='rgb(0,64,255)'
    )))

fig.update_layout(
    legend_traceorder='reversed',
    geo=go.layout.Geo(
        showframe=False,
        landcolor="rgb(229, 229, 229)",
        bgcolor='rgba(255, 255, 255, 0.0)',
        showcountries=True,
        showcoastlines=True,
        countrycolor="white",
        coastlinecolor="white",
    ))

#fig = px.scatter_geo(df, locations="iso_alpha",
#                     size="pop", # size of markers, "pop" is one of the columns of gapminder
#                     )
fig.show()
