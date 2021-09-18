import locale
from datetime import datetime

import numpy as np
import pandas as pd
import requests
# from tslearn.clustering import TimeSeriesKMeans
from sklearn.cluster import KMeans



def preprocess(csv_name):
    df = pd.read_csv(csv_name, index_col=0)
    df.legible_last_reported = df.legible_last_reported.apply(datetime.fromisoformat)
    df.lastUpdated = df.lastUpdated.apply(datetime.fromisoformat)
    df.date_retrieved = df.date_retrieved.apply(datetime.fromisoformat)
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
    loc_stations_df["rental_methods_str"] = loc_stations_df.rental_methods.apply(lambda x: x[0] if type(x) == list
    else "Aucun")

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

    group_by_geo_df = df_geo.groupby(by=['station_id', 'name', 'lat', 'lon', 'capacity',
                                         'rental_methods_str', 'Jour et heure', 'Time',
                                         TIME_VARIABLE]).agg({x: np.mean for x in metrics}).reset_index()
    group_by_geo_df = group_by_geo_df.sort_values(by=TIME_VARIABLE)

    group_by_geo_df.fillna(0, inplace=True)
    df_geo.fillna(0, inplace=True)
    return group_by_geo_df, df_geo


def clustering(df_geo):
    group_by_geo_df = df_geo.groupby(by=['name', "lat", "lon", "day_hour_of_week_num"]).agg(
        {'num_bikes_available': np.mean})

    dataset, labelled_names = [], []

    shape_max = group_by_geo_df.groupby(by=['name', "lat", "lon"]).size().values.max()

    group_by_geo_df = group_by_geo_df.reset_index("day_hour_of_week_num")

    for id_ in group_by_geo_df.index.unique():
        name = id_[0]
        x = group_by_geo_df.loc[name].num_bikes_available.to_numpy().copy()

        # Normalize

        if x.shape[0] == shape_max:
            if x.max():
                x /= x.max()
            else:
                continue
            labelled_names.append(name)
            dataset.append(x)
        else:
            pass

    dataset = np.array(dataset)
    group_by_geo_df = group_by_geo_df.reset_index()

    # model = TimeSeriesKMeans(n_clusters=3, metric="softdtw", max_iter=10)
    model = KMeans(n_clusters=3)
    model.fit(dataset)

    cluster_df = group_by_geo_df[group_by_geo_df.name.isin(labelled_names)]
    cluster_df.loc[:, "Cluster"] = cluster_df.name.apply(lambda x: str(model.labels_[labelled_names.index(x)]))

    return cluster_df, model.cluster_centers_
