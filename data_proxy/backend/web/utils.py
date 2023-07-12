import json
import influxdb_client
import requests
from influxdb_client.client.write_api import SYNCHRONOUS
from data_proxy.backend.configuration import IFD_ORG, IFD_URL, IFD_TOKEN, IFD_BUCKET, BOT_TOKEN, CHAT_ID

influx_client = influxdb_client.InfluxDBClient(
    url=IFD_URL,
    token=IFD_TOKEN,
    org=IFD_ORG
)


def get_current_config():
    data = None
    with open("sensor_config.json") as file:
        data = json.load(file)
    return data


def save_new_config(config):
    with open("sensor_config.json", "w") as file:
        json.dump(config, file)


def save_to_influx(data: dict, measurement):
    writer = influx_client.write_api(write_options=SYNCHRONOUS)
    p = influxdb_client.Point(measurement)
    for key in data.keys():
        p = p.tag(key, data[key])
    writer.write(bucket=IFD_BUCKET, org=IFD_ORG, record=p)


def logger(data):
    with open("logfile.csv", "a+") as file:
        file.write(data)


def telegram_send_message(message):
    try:
        a = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}&parse_mode=html")
        print(a)
    except Exception as e:
        pass