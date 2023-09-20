import fastapi.routing
import starlette.responses
from data_proxy.backend.web.configuration import THING_TOKEN
from data_proxy.backend.web.errors import Denied
from data_proxy.backend.web.models.edit import RssiAction, LitterUsed, TempAction, LatencyAction
from datetime import datetime
from fastapi import BackgroundTasks
from data_proxy.backend.web.utils import save_to_influx, logger, telegram_send_message
import time

router = fastapi.routing.APIRouter(
    prefix="/api/actions/v1",
    tags=[
        "Actions v1",
    ],
)

CREATED = starlette.responses.Response(content=None, status_code=201)


@router.post("/rssi",
             summary="Send data about wi-fi signal strength",
             status_code=201)
def rssi_action(*, data: RssiAction):
    if data.thing_token != THING_TOKEN:
        raise Denied
    start = datetime.now().timestamp()
    save_to_influx({'value': data.rssi_str}, "rssi")
    end = datetime.now().timestamp()
    logger(f"RSSI;{end-start};\n")
    return CREATED


@router.post("/litter_usage",
             summary="Send alert about event 'litter_in_use'",
             status_code=201)
def litter_usage_action(*, data: LitterUsed):
    if data.thing_token != THING_TOKEN:
        raise Denied
    start = datetime.now().timestamp()
    save_to_influx({'value': 1}, "litter_usage")
    end = datetime.now().timestamp()
    logger(f"LITTER;{end-start};\n")

    telegram_send_message(f"""
    🔈<b> Litterbox usage detected! </b>
    """)
    return CREATED


@router.post("/temperature", summary="Send temperature from sensor", status_code=201)
def temperature_action(*, data: TempAction):
    if data.thing_token != THING_TOKEN:
        raise Denied
    start = datetime.now().timestamp()
    save_to_influx({'value': float(data.temperature)}, "temperature")
    end = datetime.now().timestamp()
    logger(f"TMP;{end-start};\n")
    return CREATED


@router.post("/latency", summary="Send latency data from sensor", status_code=201)
def latency_action(*, data:LatencyAction):
    if data.thing_token != THING_TOKEN:
        raise Denied
    save_to_influx({'value': float(data.latency)}, "latency")
    return CREATED