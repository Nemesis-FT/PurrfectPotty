token = "mHGy7gjCUjeSdjTMN38GZ_xeDFeUF1OXRHJDiB0_OuKWt7BlF13r9mI-99ARL5Fhd5g42i7uwrhtlqYyI-uzFg=="
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
org = "purrfectpotty"
url = "http://127.0.0.1:8086"

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
bucket = "pp1"

# Define the write api
write_api = write_client.write_api(write_options=SYNCHRONOUS)

data = {
    "point1": {
        "location": "Klamath",
        "species": "bees",
        "count": 23,
    },
    "point2": {
        "location": "Portland",
        "species": "ants",
        "count": 30,
    },
    "point3": {
        "location": "Klamath",
        "species": "bees",
        "count": 28,
    },
    "point4": {
        "location": "Portland",
        "species": "ants",
        "count": 32,
    },
    "point5": {
        "location": "Klamath",
        "species": "bees",
        "count": 29,
    },
    "point6": {
        "location": "Portland",
        "species": "ants",
        "count": 40,
    },
}

for key in data:
    point = (
        Point("census")
        .tag("location", data[key]["location"])
        .field(data[key]["species"], data[key]["count"])
    )
    write_api.write(bucket=bucket, org=org, record=point)
    time.sleep(1)  # separate points by 1 second

print("Complete. Return to the InfluxDB UI.")
