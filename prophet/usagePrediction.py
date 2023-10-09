#import matplotlib.pyplot as plt
import datetime

import pandas as pd
import numpy as np
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from sklearn.linear_model import LinearRegression
from configuration import IFD_BUCKET, IFD_TOKEN, IFD_ORG, IFD_URL, BOT_TOKEN, CHAT_ID
import requests


bucket = IFD_BUCKET
org = IFD_ORG
token = IFD_TOKEN
url = IFD_URL

def telegram_send_message(message):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}&parse_mode=html")
    except Exception as e:
        print(e)


# instanza del client
client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)

query_api = client.query_api()
# query per ottenere i dati
query = 'from(bucket: "pp1") \
|> range(start: -14d)\
|> filter(fn: (r) => r["_measurement"] == "litter_usage")\
|> filter(fn: (r) => r["_field"] == "value")'

# eseguo la query
result = query_api.query(org=org, query=query)
tmp = []
for elem in result[0].records:
    tmp.append([elem.row[4].replace(tzinfo=None), elem.row[5]])

df = pd.DataFrame(tmp, columns=["ds","y"])
#print (df)


# Converti la colonna 'ds' in formato data
df['ds'] = pd.to_datetime(df['ds']).dt.date

# Raggruppa per data e somma i valori 'y'
nuovo_df = df.groupby('ds')['y'].sum().reset_index()

# Convertire le date in numeri ordinali (per utilizzarle in un modello di regressione)
nuovo_df['ds_ordinal'] = nuovo_df['ds'].apply(lambda x: x.toordinal())

# Creare il modello di regressione lineare
model = LinearRegression()

# Addestrare il modello sui dati esistenti
X = nuovo_df[['ds_ordinal']]
y = nuovo_df['y']
model.fit(X, y)

# Preparare i dati futuri per la previsione
date_futuro = pd.date_range(start=str(datetime.date.today()), end=str(datetime.date.today()+datetime.timedelta(days=1)))
date_futuro_ordinal = [date.toordinal() for date in date_futuro]

# Fare le previsioni
previsioni = model.predict(np.array(date_futuro_ordinal).reshape(-1, 1))

# Arrotondare le previsioni a numeri interi
previsioni_int = [int(round(p)) for p in previsioni]

# Creare un dataframe con le previsioni intere
previsioni_df = pd.DataFrame({'ds': date_futuro, 'y_pred': previsioni_int})
'''
# Visualizzare i risultati
plt.plot(nuovo_df['ds'], nuovo_df['y'], label='Dati Storici')
plt.plot(previsioni_df['ds'], previsioni_df['y_pred'], label='Previsioni', color='red', linestyle='--')
plt.xlabel('Data')
plt.ylabel('Valore')
plt.legend()
plt.show()

print(previsioni_df)
'''
# upload dati su influxdb
write_api = client.write_api(write_options=SYNCHRONOUS)
for idx in previsioni_df.index:
    elem = previsioni_df.iloc[idx, :]
    data = elem.ds
    value = elem.y_pred
    p = influxdb_client.Point("litter_usage")
    p.field("value", value)
    p.time(data)
    write_api.write(bucket="ppredict", org=org, record=p)
    #write_api.write(bucket="ppredict", org=org, record=forecast['y_pred'], data_frame_measurement_name='litter_usage')

# invio messaggio telegram
telegram_send_message(f"🐱 Tomorrow the litterbox will get used {previsioni_df['y_pred'][0]} time(s) 🐱")
