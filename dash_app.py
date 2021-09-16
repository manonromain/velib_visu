import locale, os
from datetime import datetime

import dash
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from dash import dcc
import dash_daq as daq
from dash import html
from flask import Flask
from dash.dependencies import Input, Output

df = pd.read_csv("velib_data_with_date.csv", index_col=0)
n_lines = df.shape[0]
df = df.drop_duplicates()
print("Dropped {} duplicates".format(n_lines - df.shape[0]))
df.to_csv("velib_data_with_date.csv")
df.legible_last_reported = df.legible_last_reported.apply(datetime.fromisoformat)
df.lastUpdated = df.lastUpdated.apply(datetime.fromisoformat)
df.date_retrieved = df.date_retrieved.apply(datetime.fromisoformat)
print(df.date_retrieved.max())
df = df.sort_values(by="last_reported")
df = df[df.is_renting == 1]

TIME_VARIABLE = "day_hour_of_week_num"

df["day_hour_of_week_num"] = df["date_retrieved"].apply(lambda x: 100 * x.weekday() + x.hour)
df["hour_num"] = df["date_retrieved"].apply(lambda x: x.hour)

locale.setlocale(locale.LC_TIME, "fr_FR")
df["Jour et heure"] = df["date_retrieved"].apply(lambda x: datetime.strftime(x, "%A %Hh"))

locale.setlocale(locale.LC_TIME, "en_US")
df["Time"] = df["date_retrieved"].apply(lambda x: datetime.strftime(x, "%A %I%p"))

req = requests.get("https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_information.json")
loc_stations_data = req.json()["data"]["stations"]
loc_stations_df = pd.DataFrame(loc_stations_data)
loc_stations_df["rental_methods_str"] = loc_stations_df.rental_methods.apply(lambda x: x[0]
if type(x) == list else "Aucun")

df_geo = df.merge(loc_stations_df, on="station_id")
df_geo = df_geo.sort_values(by='date_retrieved')
df_geo["date"] = df_geo.date_retrieved.astype(str)

# Creating metrics
df_geo["diff_ebikes"] = df_geo.groupby(by=['stationCode_x']).num_ebikes_available.diff()
df_geo["diff_mech_bikes"] = df_geo.groupby(by=['stationCode_x']).num_mech_bikes_available.diff()
df_geo["diff_bikes"] = df_geo.groupby(by=['stationCode_x']).num_bikes_available.diff()
df_geo["occupancy"] = df_geo.num_bikes_available / df_geo.capacity
df_geo["occupancy_mech"] = df_geo.num_mech_bikes_available / df_geo.capacity
df_geo["occupancy_ebikes"] = df_geo.num_ebikes_available / df_geo.capacity
df_geo["frac_mech"] = df_geo.num_mech_bikes_available / df_geo.num_bikes_available
df_geo["frac_ebikes"] = df_geo.num_ebikes_available / df_geo.num_bikes_available

# Aggregate by timeframe and stations
metrics = ['num_bikes_available',
           'num_docks_available',
           'num_mech_bikes_available',
           'num_ebikes_available',
           'occupancy',
           'occupancy_mech',
           'occupancy_ebikes',
           'frac_mech',
           'frac_ebikes',
           'diff_ebikes',
           'diff_mech_bikes'
           ]

pretty_names_EN = {'num_bikes_available': 'Number of available bikes',
                   'num_docks_available': 'Number of available docks',
                   'num_mech_bikes_available': 'Number of available mechanical bikes',
                   'num_ebikes_available': 'Number of available electrical bikes',
                   'occupancy': 'Occupancy rate',
                   'occupancy_mech': 'Occupancy rate (only mechanical)',
                   'occupancy_ebikes': 'Occupancy rate (only electrical)',
                   'frac_mech': 'Fraction of mechanical bikes',
                   'frac_ebikes': 'Fraction of electrical bikes',
                   'diff_ebikes': 'Difference by timeframe (only electrical)',
                   'diff_mech_bikes': 'Difference by timeframe (only mechanical)',
                   }

pretty_names_FR = {'num_bikes_available': 'Nombre de vélos disponibles',
                   'num_docks_available': 'Nombre de places libres',
                   'num_mech_bikes_available': 'Nombre de vélos mécaniques disponibles',
                   'num_ebikes_available': 'Nombre de vélos êlectriques disponibles',
                   'occupancy': "Taux d'occupation",
                   'occupancy_mech': "Taux d'occupation (seulement mécanique)",
                   'occupancy_ebikes': "Taux d'occupation (seulement électrique)",
                   'frac_mech': "Pourcentage de vélos mécaniques",
                   'frac_ebikes': "Pourcentage de vélos électriques",
                   'diff_ebikes': 'Différence par pas de temps (seulement électrique)',
                   'diff_mech_bikes': 'Différence par pas de temps (seulement mécanique)',
                   }

group_by_geo_df = df_geo.groupby(by=['station_id', 'name', 'lat', 'lon', 'capacity',
                                     'rental_methods_str', 'Jour et heure', 'Time',
                                     TIME_VARIABLE]).agg({x: np.mean for x in metrics}).reset_index()

group_by_geo_df = group_by_geo_df.sort_values(by=TIME_VARIABLE)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = Flask(__name__)
server.secret_key = os.environ.get('secret_key', 'secret')
app = dash.Dash(name = __name__, server=server, suppress_callback_exceptions = True)

app.layout = html.Div(children=[
    html.Div(className="row",
             children=[html.H1(children='Velib Visualisation'),

                       html.Div([
                           # [html.Label(id="lang-label"),
                           #  dcc.RadioItems(
                           #      id='language',
                           #      options=[
                           #          {'label': 'English', 'value': 'EN'},
                           #          {'label': u'Français', 'value': 'FR'}
                           #      ],
                           #      value='EN'
                           #  ),
                            daq.ToggleSwitch(
                                id='in_french',
                                label=['English', 'Français'],
                                style={'width': '250px', 'margin': 'auto'},
                                value=False
                            ),
                            ],
                           style={'width': '10%', 'display': 'inline-block'})
                       ]),


    html.Div(
        [html.Div(className="row",
                  children=[html.Label('Metrics', id="metrics-label"),
                            dcc.Dropdown(
                                id='yaxis-column',
                                value='frac_ebikes'
                            )],
                  style={'width': '20%', 'display': 'inline-block'})
            ,
         html.Div(
             [html.Label(id="size-label"),
              dcc.Dropdown(
                  id='size-column',
                  value='num_bikes_available'
              )],
             style={'width': '20%', 'display': 'inline-block'}),
         html.Div(
             [html.Label('Mode'),
              dcc.RadioItems(
                  id='mode-plot',
                  options=[
                      {'label': 'Scatter', 'value': 'Scatter'},
                      {'label': 'Density', 'value': 'Density'}
                  ],
                  value='Scatter'
              )],
             style={'width': '10%', 'display': 'inline-block'}),
         ]),
    html.Div(className="row",
             children=[
                 html.Div(dcc.Graph(id='main-graphic'), style={'width': '60%', 'display': 'inline-block'}),
                 html.Div(dcc.Graph(id='specific-graphic'), style={'width': '40%', 'display': 'inline-block'})])
])


@app.callback(
    Output('yaxis-column', 'options'),
    Output('size-column', 'options'),
    Output('mode-plot', 'options'),
    Output('size-label', 'children'),
    Output('metrics-label', 'children'),
    Input('in_french', 'value'))
def update_language(in_french):
    if in_french:
        options_y = [{"label": pretty_names_FR[x], "value": x} for x in metrics]
        options_mode = [
            {'label': 'Nuage de points', 'value': 'Scatter'},
            {'label': 'Densité', 'value': 'Density'}
        ]
        size_label = "Rayon"
        metrics_label = "Mesure"
    else:
        options_y = [{"label": pretty_names_EN[x], "value": x} for x in metrics]
        options_mode = [
            {'label': 'Scatter', 'value': 'Scatter'},
            {'label': 'Density', 'value': 'Density'}
        ]
        size_label = "Radius"
        metrics_label = "Metric"
    return options_y, options_y, options_mode, size_label, metrics_label


@app.callback(
    Output('main-graphic', 'figure'),
    Input('in_french', 'value'),
    Input('mode-plot', 'value'),
    Input('yaxis-column', 'value'),
    Input('size-column', 'value'))
def update_graph(in_french, mode_plot, yaxis_column_name, size_column_name):
    print("updated", in_french)
    rescale_size = np.abs(group_by_geo_df[size_column_name])
    rescale_size = (rescale_size - rescale_size.min()) / (rescale_size.max() - rescale_size.min())
    if in_french:
        local_day_hour = "Jour et heure"
        labels = pretty_names_FR
    else:
        local_day_hour = "Time"
        labels = pretty_names_EN

    #FIXME
    #local_day_hour = TIME_VARIABLE

    if mode_plot == "Density":
        rescale_size += 1
        rescale_size *= 6
        fig = px.density_mapbox(group_by_geo_df, lat="lat", lon="lon", z=yaxis_column_name, radius=rescale_size,
                                color_continuous_scale=px.colors.sequential.solar,
                                hover_name="name", hover_data=["num_bikes_available", "capacity"],
                                zoom=10, range_color=[0, group_by_geo_df[yaxis_column_name].max()],
                                labels=labels,
                                animation_frame=local_day_hour, animation_group="name")
    else:
        fig = px.scatter_mapbox(group_by_geo_df, lat="lat", lon="lon", color=yaxis_column_name, size=size_column_name,
                                color_continuous_scale=px.colors.sequential.solar,
                                hover_name="name", hover_data=["num_bikes_available", "capacity"],
                                zoom=10, range_color=[0, group_by_geo_df[yaxis_column_name].max()],
                                labels=labels,
                                animation_frame=local_day_hour, animation_group="name")  # , width=800, height=800)

    fig.update_layout(clickmode='event+select')
    fig.update_layout(mapbox_style="carto-positron")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig


@app.callback(
    Output('specific-graphic', 'figure'),
    Input('in_french', 'value'),
    #Input('yaxis-column', 'value'),
    Input('main-graphic', 'clickData'))
def display_click_data(in_french, clickData):
    yaxis_column_name = "num_bikes_available"
    if clickData:
        data = clickData["points"][0]

        if in_french:
            y_label = pretty_names_FR[yaxis_column_name]
            title = "{} à {}".format(y_label, data["hovertext"])
        else:
            y_label = pretty_names_EN[yaxis_column_name]
            title = "{} in {}".format(y_label, data["hovertext"])

        dff = df_geo[(df_geo.lat == data["lat"]) & (df_geo.lon == data["lon"])]

        fig = px.scatter(dff, x="date_retrieved", y=yaxis_column_name,
                         title=title, labels={"date_retrieved": "",
                                              yaxis_column_name: y_label})

        return fig
    else:
        if in_french:
            text_none = "Cliquez sur une station pour voir les données"
        else:
            text_none = "Click on a station to see all datapoints"

        fig = go.Figure()
        fig.update_layout(
            xaxis={"visible": False},
            yaxis={"visible": False},
            annotations=[
                {
                    "text":text_none,
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        )

        return fig



if __name__ == "__main__":
    app.run_server(host='127.0.0.1', debug=True)
