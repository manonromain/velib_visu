import sys
import time
from datetime import datetime

import pandas as pd
import requests


def request_and_write():
    req = requests.get("https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_status.json")
    data = req.json()

    df = pd.DataFrame(data["data"]["stations"])

    # Preprocess
    df["num_mech_bikes_available"] = df.num_bikes_available_types.apply(lambda x: x[0]["mechanical"])
    df["num_ebikes_available"] = df.num_bikes_available_types.apply(lambda x: x[1]["ebike"])
    df["legible_last_reported"] = df.last_reported.apply(datetime.fromtimestamp)
    df["functioning_word"] = df.is_installed.apply(str) + df.is_returning.apply(str) + df.is_renting.apply(str)
    df = df.drop(["numBikesAvailable", "numDocksAvailable", "num_bikes_available_types"], axis=1)
    df["lastUpdated"] = datetime.fromtimestamp(data["lastUpdatedOther"])
    df["date_retrieved"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df.to_csv("velib_data_with_date.csv", mode="a", header=False)
    return 0


if __name__ == "__main__":
    while True:
        try:
            request_and_write()
        except Exception as e:
            sys.stdout.write(e)
            time.sleep(60)
            continue
        for remaining in range(15 * 60, 0, -1):
            sys.stdout.write("\r")
            sys.stdout.write("{:2d} seconds remaining.".format(remaining))
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\rAgain!            \n")
