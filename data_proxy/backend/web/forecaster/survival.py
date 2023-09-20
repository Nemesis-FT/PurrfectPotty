import pandas as pd
from lifelines import CoxPHFitter
import pandas as pd
from prophet import Prophet
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from data_proxy.backend.web.configuration import IFD_BUCKET, IFD_TOKEN, IFD_ORG, IFD_URL
import datetime
import matplotlib as plt

bucket = IFD_BUCKET
org = IFD_ORG
token = IFD_TOKEN
url = IFD_URL

client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)

query_api = client.query_api()
# query per ottenere i dati
query = 'from(bucket: "pp1") \
    |> range(start: -2d)\
    |> filter(fn: (r) => r["_measurement"] == "litter_usage")\
    |> filter(fn: (r) => r["_field"] == "value")' \
    # eseguo la query
result = query_api.query(org=org, query=query)

tmp = []
data = []
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
survival_functions = cph.predict_median(X)

import datetime
print(f"Percentile: {cph.predict_percentile(X, p=0.7)}, {datetime.datetime.now()+datetime.timedelta(seconds=cph.predict_percentile(X, p=0.7))};")
print(f"Median: {cph.predict_median(X)}, {datetime.datetime.now()+datetime.timedelta(seconds=cph.predict_median(X))};")
print(datetime.datetime.now()+datetime.timedelta(seconds=cph.predict_median(X)))
