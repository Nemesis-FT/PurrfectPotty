import json


def get_current_config():
    data = None
    with open("sensor_config.json") as file:
        data = json.load(file)
    return data


def save_new_config(config):
    with open("sensor_config.json", "w") as file:
        json.dump(config, file)