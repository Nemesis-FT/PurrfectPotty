import fastapi.routing
import starlette.responses
from fastapi import Depends
from data_proxy.backend.configuration import THING_TOKEN
from data_proxy.backend.web.errors import Denied
from data_proxy.backend.web.models.edit import RssiAction, LitterUsed, LitterEmpty
from datetime import datetime
from fastapi import BackgroundTasks
from data_proxy.backend.web.utils import save_to_influx, logger, telegram_send_message

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
def rssi_action(*, data: RssiAction, tasker: BackgroundTasks):
    if data.thing_token != THING_TOKEN:
        raise Denied
    save_to_influx({'value': data.rssi_str}, "rssi")
    tasker.add_task(logger, f"RSSI;{datetime.now().timestamp()};{data.timestamp}\n")
    return CREATED


@router.post("/litter_usage",
             summary="Send alert about event 'litter_in_use'",
             status_code=201)
def litter_usage_action(*, data: LitterUsed, tasker: BackgroundTasks):
    if data.thing_token != THING_TOKEN:
        raise Denied
    save_to_influx({'value': 1}, "litter_usage")
    tasker.add_task(logger, f"LU;{datetime.now().timestamp()};{data.timestamp}\n")
    tasker.add_task(telegram_send_message, f"""
    🔈<b> Litterbox usage detected! </b>
    """)
    return CREATED


@router.post("/litter_alarm",
             summary="Send alert about event 'litter_empty'",
             status_code=201)
def litter_alarm_action(*, data: LitterEmpty, tasker: BackgroundTasks):
    if data.thing_token != THING_TOKEN:
        raise Denied
    save_to_influx({'value': 1}, "litter_alarm")
    tasker.add_task(logger, f"LA;{datetime.now().timestamp()};{data.timestamp}\n")
    tasker.add_task(telegram_send_message, f"""
    🚨<b> Warning! Litterbox almost empty! </b> 🚨
    """)
    return CREATED
