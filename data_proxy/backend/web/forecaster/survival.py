from lifelines import CoxPHFitter
import pandas as pd
import influxdb_client
from data_proxy.backend.web.configuration import IFD_BUCKET, IFD_TOKEN, IFD_ORG, IFD_URL
import datetime
from data_proxy.backend.web.utils import telegram_send_message

bucket = IFD_BUCKET
org = IFD_ORG
token = IFD_TOKEN
url = IFD_URL


def run_analysis():
    client = influxdb_client.InfluxDBClient(
        url=url,
        token=token,
        org=org
    )

    query_api = client.query_api()
    query = 'from(bucket: "pp1") \
        |> range(start: -7d)\
        |> filter(fn: (r) => r["_measurement"] == "litter_usage")\
        |> filter(fn: (r) => r["_field"] == "value")'
    result = query_api.query(org=org, query=query)
    tmp = []
    oldelem = None
    for elem in result[0].records:
        if not oldelem:
            oldelem = elem.row[4].replace(tzinfo=None)
            continue
        tmp.append(int((elem.row[4].replace(tzinfo=None) - oldelem).total_seconds()))
        oldelem = elem.row[4].replace(tzinfo=None)
    df = pd.DataFrame({"observed": [True for i in tmp],
                       "duration": tmp})
    cph = CoxPHFitter()
    cph.fit(df, "duration", "observed")

    X = pd.DataFrame(index=["sub1"])
    lower = (datetime.datetime.now() + datetime.timedelta(seconds=cph.predict_median(X)) + datetime.timedelta(hours=-1))
    upper = (datetime.datetime.now() + datetime.timedelta(seconds=cph.predict_median(X)) + datetime.timedelta(hours=1))
    telegram_send_message(
        f"Prossimo utilizzo: tra {lower.hour}:{lower.minute} e {upper.hour}:{upper.minute}")
