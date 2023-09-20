import pandas as pd
from prophet import Prophet
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from data_proxy.backend.web.configuration import IFD_BUCKET, IFD_TOKEN, IFD_ORG, IFD_URL
import datetime

bucket = IFD_BUCKET
org = IFD_ORG
token = IFD_TOKEN
url = IFD_URL


def get_forecast(periods, measurement):
    # instanza del client
    client = get_ifd_client()
    query_api = client.query_api()
    # query per ottenere i dati
    query = f'from(bucket: "{bucket}") \
    |> range(start: -30d)\
    |> filter(fn: (r) => r["_measurement"] == "{measurement}")\
    |> filter(fn: (r) => r["_field"] == "value")' \
            '|> aggregateWindow(every: 1h, fn: mean, createEmpty:false)' \
        # eseguo la query
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
    future = model.make_future_dataframe(periods=periods, freq="H")
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


if __name__ == "__main__":
    predictions = {"temperature": [], "latency": []}
    client = get_ifd_client()
    for key in predictions.keys():
        pred: pd.DataFrame = get_forecast(6, key)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        for idx in range(len(pred)):
            print("OK")
            time, elem = pred.iloc[idx]
            p = influxdb_client.Point(key)
            p.field("value", elem)
            p.time(time-datetime.timedelta(hours=2))
            write_api.write(bucket="ppredict", org=org, record=p)
        write_api.close()

    print(predictions)
