#!/usr/bin/env python3
import sqlite3
from glob import iglob
from os import environ, path
from tempfile import TemporaryDirectory

import kagglehub
import pandas as pd


TABLE_ID_MAP = {
    'circuits': {
        'circuitId': 'id',
    },
    'status': {
        'statusId': 'id',
    },
    'drivers': {
        'driverId': 'id',
    },
    'races': {
        'raceId': 'id',
    },
    'constructors': {
        'constructorId': 'id',
    },
    'constructor_standings': {
        'constructorStandingsId': 'id',
    },
    'qualifying': {
        'qualifyId': 'id',
    },
    'driver_standings': {
        'driverStandingsId': 'id',
    },
    'constructor_results': {
        'constructorResultsId': 'id',

    },
    'results': {
        'resultId': 'id',
    },
}


def download_data():
    conn = sqlite3.connect("data.db")

    with TemporaryDirectory() as tmp:
        environ["KAGGLEHUB_CACHE"] = tmp
        data_dir = kagglehub.dataset_download(
            "rohanrao/formula-1-world-championship-1950-2020"
        )
        for csv in iglob(data_dir + "/*.csv"):
            df = pd.read_csv(csv)
            table_name = path.splitext(path.basename(csv))[0]
            df = df.rename(columns=TABLE_ID_MAP.get(table_name, {}))
            df.columns = [
                ''.join([
                    '_' + c.lower() if c.isupper() else c 
                    for c in col
                ])
                for col in df.columns
            ]
            print(table_name)
            df.to_sql(table_name, conn, if_exists="replace", index=False)


if __name__ == "__main__":
    print("Downloading data...")
    download_data()
