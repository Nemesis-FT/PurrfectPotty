#import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from sklearn.linear_model import LinearRegression
from data_proxy.backend.web.configuration import IFD_BUCKET, IFD_TOKEN, IFD_ORG, IFD_URL
from data_proxy.backend.web.utils import telegram_send_message


bucket = IFD_BUCKET
org = IFD_ORG
token = IFD_TOKEN
url = IFD_URL


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

print(nuovo_df)

# Convertire le date in numeri ordinali (per utilizzarle in un modello di regressione)
nuovo_df['ds_ordinal'] = nuovo_df['ds'].apply(lambda x: x.toordinal())

# Creare il modello di regressione lineare
model = LinearRegression()

# Addestrare il modello sui dati esistenti
X = nuovo_df[['ds_ordinal']]
y = nuovo_df['y']
model.fit(X, y)

# Preparare i dati futuri per la previsione
date_futuro = pd.date_range(start='2023-09-22', end='2023-09-25')
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
for forecast in previsioni_df:
    write_api.write(bucket="ppredict", org=org, record=forecast['y_pred'], data_frame_measurement_name='litter_usage')

# invio messaggio telegram
telegram_send_message(f"🐱 Domani sono previsti ben {previsioni_df['y_pred'][0]} utilizzi 🐱")
