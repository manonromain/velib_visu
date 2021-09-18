import locale

import dash
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output

from data_process import preprocess, clustering
from layout import LAYOUT

NAME_CSV = "velib_data_with_date.csv"

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

group_by_geo_timeslice_df, df_geo = preprocess(NAME_CSV)
cluster_df, cluster_centers = clustering(df_geo)
date_last_updated = df_geo.date_retrieved.max()

# Theme

color_theme = {
    "text": "gray",
    "bg": "#F6F6F4",
    "primary": "#45B69C",
    "accent1": "#FC7753",
    "continuous_scale": ["#112C26", "#45B69C", "#FC7753"],
    "discrete_scale": {"0": "#F093F0", "1":"#45B69C", "2":"#FC7753"}
}

app = dash.Dash(name=__name__, title="Manon's Velib")
server = app.server

app.layout = LAYOUT


@app.callback(
    Output('yaxis-column', 'options'),
    Output('size-column', 'options'),
    Output('mode-plot', 'options'),
    Output('size-label', 'children'),
    Output('metrics-label', 'children'),
    Output('last-updated', 'children'),
    Input('in_french', 'value'))
def update_language(in_french):
    if in_french:
        options_y = [{"label": pretty_names_FR[x], "value": x} for x in metrics]
        options_mode = [
            {'label': 'Nuage de points', 'value': 'Scatter'},
            {'label': 'Densité', 'value': 'Density'}
        ]
        size_label = "Rayon"
        metrics_label = "Couleur"
        locale.setlocale(locale.LC_TIME, "fr_FR")
        last_updated_text = "Dernière mise à jour : {} à {}".format(date_last_updated.strftime("%d %B %Y"),
                                                                    date_last_updated.strftime("%Hh%M"))
    else:
        options_y = [{"label": pretty_names_EN[x], "value": x} for x in metrics]
        options_mode = [
            {'label': 'Scatter', 'value': 'Scatter'},
            {'label': 'Density', 'value': 'Density'}
        ]
        size_label = "Radius"
        metrics_label = "Color"
        locale.setlocale(locale.LC_TIME, "en_US")
        last_updated_text = "Last updated : {} at {}".format(date_last_updated.strftime("%B %d, %Y"),
                                                             date_last_updated.strftime("%H:%M"))
    return options_y, options_y, options_mode, size_label, metrics_label, last_updated_text


@app.callback(
    Output('main-graphic', 'figure'),
    Input('in_french', 'value'),
    Input('mode-plot', 'value'),
    Input('yaxis-column', 'value'),
    Input('size-column', 'value'))
def update_graph(in_french, mode_plot, yaxis_column_name, size_column_name):
    rescale_size = np.abs(group_by_geo_timeslice_df[size_column_name])
    rescale_size = (rescale_size - rescale_size.min()) / (rescale_size.max() - rescale_size.min())
    if in_french:
        local_day_hour = "Jour et heure"
        labels = pretty_names_FR
    else:
        local_day_hour = "Time"
        labels = pretty_names_EN

    # FIXME
    # local_day_hour = TIME_VARIABLE

    if mode_plot == "Density":
        rescale_size += 1
        rescale_size *= 6
        fig = px.density_mapbox(group_by_geo_timeslice_df, lat="lat", lon="lon", z=yaxis_column_name,
                                radius=rescale_size,
                                hover_name="name", hover_data=["num_bikes_available", "capacity"],
                                zoom=10, range_color=[0, group_by_geo_timeslice_df[yaxis_column_name].max()],
                                labels=labels, color_continuous_scale=color_theme["continuous_scale"],
                                animation_frame=local_day_hour, animation_group="name")
    else:
        fig = px.scatter_mapbox(group_by_geo_timeslice_df, lat="lat", lon="lon", color=yaxis_column_name,
                                size=size_column_name,
                                hover_name="name", hover_data=["num_bikes_available", "capacity"],
                                zoom=10, range_color=[0, group_by_geo_timeslice_df[yaxis_column_name].max()],
                                labels=labels, color_continuous_scale=color_theme["continuous_scale"],
                                animation_frame=local_day_hour, animation_group="name")  # , width=800, height=800)

    fig.update_layout(clickmode='event+select')
    fig.update_layout(mapbox_style="carto-positron")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    fig.update_layout(
        font_family="Trebuchet MS",
        font_color=color_theme["text"],
        paper_bgcolor=color_theme["bg"],
    )

    return fig


@app.callback(
    Output('specific-graphic', 'figure'),
    Input('in_french', 'value'),
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
                         title=title, labels={"date_retrieved": "", yaxis_column_name: y_label})

        fig.update_traces(marker=dict(color=color_theme["primary"]))

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
                    "text": text_none,
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        )

    fig.update_layout(
        font_family="Trebuchet MS",
        font_color=color_theme["text"],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor=color_theme["bg"],
    )
    return fig


@app.callback(
    Output('clustering-graphic', 'figure'),
    Input('in_french', 'value'),
    Input('yaxis-column', 'value'))
def update_clustering_graph(in_french, yaxis_column_name):
    if in_french:
        labels = pretty_names_FR
    else:
        labels = pretty_names_EN

    fig = px.scatter_mapbox(cluster_df, lat="lat", lon="lon", color="Cluster",
                            color_discrete_map=color_theme["discrete_scale"],
                            hover_name="name", hover_data=["num_bikes_available"],
                            zoom=10, labels=labels)

    fig.update_layout(clickmode='event+select')
    fig.update_layout(mapbox_style="carto-positron")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    fig.update_layout(
        font_family="Trebuchet MS",
        font_color=color_theme["text"],
        paper_bgcolor=color_theme["bg"],
    )

    return fig


@app.callback(
    Output('specific-clustering-graphic', 'figure'),
    Input('in_french', 'value'),
    Input('clustering-graphic', 'clickData'))
def display_click_data_clustering(in_french, clickData):
    yaxis_column_name = "num_bikes_available"
    if clickData:
        data = clickData["points"][0]
        name = data["hovertext"]

        if in_french:
            local_day_hour = "Jour et heure"
            y_label = pretty_names_FR[yaxis_column_name]
            title = "{} à {}".format(y_label, name)
            labels = pretty_names_FR
        else:
            local_day_hour = "Time"
            y_label = pretty_names_EN[yaxis_column_name]
            title = "{} in {}".format(y_label, name)
            labels = pretty_names_EN

        dff = group_by_geo_timeslice_df[(group_by_geo_timeslice_df.lat == data["lat"])
                                        & (group_by_geo_timeslice_df.lon == data["lon"])]

        id_cluster = cluster_df[cluster_df.name == name].Cluster.unique()[0]

        x_data = dff[local_day_hour].to_numpy()
        y_data = dff[yaxis_column_name].to_numpy()
        center = cluster_centers[int(id_cluster)]

        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig.add_trace(
            go.Scatter(x=x_data, y=y_data, name="Data available", mode="markers",
                       marker=dict(color=color_theme["discrete_scale"][id_cluster]))
        )

        fig.add_trace(
            go.Scatter(x=x_data, y=center, name="Cluster center", mode='lines',
                       line=dict(color=color_theme["discrete_scale"][id_cluster])),
            secondary_y=True
        )

        fig.update_layout(title=title)

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
                    "text": text_none,
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        )

    fig.update_layout(
        font_family="Trebuchet MS",
        font_color=color_theme["text"],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor=color_theme["bg"],
    )
    return fig


if __name__ == "__main__":
    app.run_server() #debug=True, host='127.0.0.1')
