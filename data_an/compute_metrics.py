import pandas as pd
from prophet import Prophet
import influxdb_client
from configuration import IFD_BUCKET, IFD_TOKEN, IFD_ORG, IFD_URL

bucket = IFD_BUCKET
org = IFD_ORG
token = IFD_TOKEN
url = IFD_URL


def get_ifd_client():
    client = influxdb_client.InfluxDBClient(
        url=url,
        token=token,
        org=org
    )
    return client


def compute_mad(real, predicted):
    if len(real) != len(predicted):
        real = real[-len(predicted):]
    acc = 0
    for idx in range(len(real)-1):
        acc += abs(real[idx]-predicted[idx])
    return acc/len(predicted)

def compute_mse(real, predicted):
    if len(real) != len(predicted):
        real = real[-len(predicted):]
    acc = 0
    for idx in range(len(real)-1):
        acc += pow(real[idx]-predicted[idx], 2)
    return acc/len(predicted)


def run():
    list = ["litter_usage", "litter_usage_prophet", "temperature"]
    client = get_ifd_client()
    query_api = client.query_api()
    for elem in list:
        print(elem)
        if elem == "temperature":
            query_real = f'from(bucket: "pp1") \
                |> range(start: -30d)\
                |> filter(fn: (r) => r["_measurement"] == "{elem}")\
                |> filter(fn: (r) => r["_field"] == "value")' \
                         '|> aggregateWindow(every: 1d, fn: mean, createEmpty:false)'
            query_predicted = f'from(bucket: "ppredict") \
                |> range(start: -30d)\
                |> filter(fn: (r) => r["_measurement"] == "{elem}")\
                |> filter(fn: (r) => r["_field"] == "value")'

        else:
            query_real = f'from(bucket: "pp1") \
                |> range(start: -30d)\
                |> filter(fn: (r) => r["_measurement"] == "litter_usage")\
                |> filter(fn: (r) => r["_field"] == "value")' \
                         '|> aggregateWindow(every: 1d, fn: sum, createEmpty:false)' \
                         '|> yield(name: "sum")'
            query_predicted = f'from(bucket: "ppredict") \
                |> range(start: -30d)\
                |> filter(fn: (r) => r["_measurement"] == "{elem}")\
                |> filter(fn: (r) => r["_field"] == "value")'
        result_real = query_api.query(org=org, query=query_real)
        result_predicted = query_api.query(org=org, query=query_predicted)
        result_real_arr = [elem.row[5] for elem in result_real[0].records]
        result_predicted_arr = [elem.row[5] for elem in result_predicted[0].records]
        print(f"MAD: {compute_mad(result_real_arr, result_predicted_arr)}")
        print(f"MSE: {compute_mse(result_real_arr, result_predicted_arr)}")


if __name__ == "__main__":
    run()
