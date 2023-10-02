import pandas as pd
from prophet import Prophet
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from configuration import IFD_BUCKET, IFD_TOKEN, IFD_ORG, IFD_URL, BOT_TOKEN, CHAT_ID
import datetime
import requests
import sys

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
                '|> aggregateWindow(every: 1h, fn: mean, createEmpty:false)' \
            # eseguo la query
    else:
        query = f'from(bucket: "{bucket}") \
            |> range(start: -14d)\
            |> filter(fn: (r) => r["_measurement"] == "{measurement}")\
            |> filter(fn: (r) => r["_field"] == "value")' \
           '|> aggregateWindow(every: 1d, fn: sum, createEmpty:false)'
    result = query_api.query(org=org, query=query)
    tmp = []
    for elem in result[0].records:
        tmp.append([elem.row[4].replace(tzinfo=None) + datetime.timedelta(hours=2), elem.row[5]])
        # tmp.append([elem.row[4].replace(tzinfo=None), elem.row[5]])
    # converto il risultato in dataframe
    df = pd.DataFrame(tmp, columns=["ds", "y"])
    df['ds'] = df['ds'].values.astype("datetime64[ns]")
    df.set_index("ds")
    model = Prophet(interval_width=1)
    model.fit(df)
    # Creazione e Fitting del modello per la predizione
    if measurement != "litter_usage":
        freq = "H"
    else:
        freq = "D"
    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)
    # Stampo il risultato del forecasting
    # upload dati su influxdb
    # write_api = client.write_api(write_options=SYNCHRONOUS)
    # write_api.write(bucket="ppredict", org=org, record=forecast, data_frame_measurement_name='litter_usage')
    forecast = forecast.tail(periods)[['ds', 'yhat']]
    return forecast


def get_ifd_client():
    client = influxdb_client.InfluxDBClient(
        url=url,
        token=token,
        org=org
    )
    return client


def telegram_send_message(message):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}&parse_mode=html")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    predictions = {"temperature": "temperatura"}
    if len(sys.argv) > 1:
        predictions = {"litter_usage": "usi lettiera"}
    client = get_ifd_client()
    for key in predictions.keys():
        if key == "litter_usage":
            pred: pd.DataFrame = get_forecast(1, key)
            res_string = f"Predizione di {predictions[key]} di domani:\n"
        else:
            pred: pd.DataFrame = get_forecast(6, key)
            res_string = f"Predizione di {predictions[key]} nelle prossime 6 ore:\n"
        write_api = client.write_api(write_options=SYNCHRONOUS)

        for idx in range(len(pred)):
            time, elem = pred.iloc[idx]
            if key == "litter_usage":
                p = influxdb_client.Point("litter_usage_prophet")
                p.field("value", float(int(elem)))
                rounding = 0
                p.time(time)
            else:
                p = influxdb_client.Point(key)
                p.field("value", elem)
                rounding = 2
                p.time(time)
            write_api.write(bucket="ppredict", org=org, record=p)
            res_string += f"{round(elem,rounding)}\n"
        write_api.close()
        telegram_send_message(res_string)

