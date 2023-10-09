from lifelines import CoxPHFitter
import pandas as pd
import influxdb_client
from data_proxy.backend.web.configuration import IFD_BUCKET, IFD_TOKEN, IFD_ORG, IFD_URL
import datetime
from lifelines import KaplanMeierFitter
from lifelines.utils import median_survival_times

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
        |> range(start: -14d)\
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
    kmf = KaplanMeierFitter()
    kmf.fit(df["duration"], df["observed"])

    median = datetime.timedelta(seconds=kmf.median_survival_time_)
    confidence_interval = median_survival_times(kmf.confidence_interval_).iloc[0]

    upper = confidence_interval[1]
    lower = confidence_interval[0]

    curr_time = datetime.datetime.now() + datetime.timedelta(hours=2)
    max = (curr_time + median)
    lower = (curr_time + datetime.timedelta(seconds=lower))
    upper = (curr_time + datetime.timedelta(seconds=upper))
    telegram_send_message(
        f"Next usage between {lower.hour}:{lower.minute} and {upper.hour}:{upper.minute}, probability peak at {max.hour}:{max.minute}.")


if __name__ == "__main__":
    run_analysis()
