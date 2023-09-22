import json
import influxdb_client
import requests
from influxdb_client.client.write_api import SYNCHRONOUS
from data_proxy.backend.web.configuration import IFD_ORG, IFD_URL, IFD_TOKEN, IFD_BUCKET, BOT_TOKEN, CHAT_ID, \
    MQTT_BROKER, MQTT_PASSWORD, MQTT_USERNAME
from paho.mqtt.client import Client

influx_client = influxdb_client.InfluxDBClient(
    url=IFD_URL,
    token=IFD_TOKEN,
    org=IFD_ORG
)


def config_updater(config: dict):
    """
    Order: sampling_rate, use_counter, used_offset, tare_timeout, danger_threshold, danger_counter
    :param config:
    :return:
    """
    client = Client("data_proxy")
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.connect(MQTT_BROKER)
    client.loop_start()
    msg = ""
    for key in config.keys():
        msg += str(config[key]["value"]) + ";"
    client.publish(topic="esp32/config", payload=msg[:-1], retain=True)
    client.loop_stop()
    client.disconnect()


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
        p = p.field(key, data[key])
    writer.write(bucket=IFD_BUCKET, org=IFD_ORG, record=p)
    writer.close()


def telegram_send_message(message):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}&parse_mode=html")
    except Exception as e:
        print(e)
