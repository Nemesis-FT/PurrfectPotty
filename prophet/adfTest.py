from statsmodels.tsa.stattools import adfuller
import pandas as pd
from prophet import Prophet
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from configuration import IFD_BUCKET, IFD_TOKEN, IFD_ORG, IFD_URL, BOT_TOKEN, CHAT_ID
import datetime
import requests

bucket = IFD_BUCKET
org = IFD_ORG
token = IFD_TOKEN
url = IFD_URL


def get_forecast(periods, measurement):
    # instanza del client
    client = get_ifd_client()
    query_api = client.query_api()
    # query per ottenere i dati
    if measurement != "litter_usage":
        query = f'from(bucket: "{bucket}") \
        |> range(start: -30d)\
        |> filter(fn: (r) => r["_measurement"] == "{measurement}")\
        |> filter(fn: (r) => r["_field"] == "value")' \
                '|> aggregateWindow(every: 1h, fn: mean, createEmpty:false)'
    else:
        query = f'from(bucket: "{bucket}") \
        |> range(start: -30d)\
        |> filter(fn: (r) => r["_measurement"] == "{measurement}")\
        |> filter(fn: (r) => r["_field"] == "value")' \
       '|> aggregateWindow(every: 1d, fn: sum, createEmpty:false)'
    result = query_api.query(org=org, query=query)
    y = []
    for elem in result[0].records:
        y.append(elem.row[5])
    res = adfuller(y)
    print(f"ADF Statistic: {res[0]}, p-value: {res[1]}, {res}")


def get_ifd_client():
    client = influxdb_client.InfluxDBClient(
        url=url,
        token=token,
        org=org
    )
    return client


if __name__ == "__main__":
    predictions = {"temperature": "temperatura", "latency": "latenza", "litter_usage": "litter_usage"}
    for key in predictions.keys():
        print(key)
        get_forecast(6, key)


