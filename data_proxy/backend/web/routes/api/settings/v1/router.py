import bcrypt
import fastapi.routing
from fastapi import Depends
from data_proxy.backend.web.authentication import get_current_user
from data_proxy.backend.web.errors import Denied
from data_proxy.backend.web.models.edit import SettingsEdit
from data_proxy.backend.web.crud import *
from data_proxy.backend.web.utils import save_new_config, get_current_config

router = fastapi.routing.APIRouter(
    prefix="/api/settings/v1",
    tags=[
        "Settings v1",
    ],
)


@router.get("/",
            summary="Get data about current configuration",
            status_code=200, response_model=SettingsEdit)
def setting_get(*, current_user=Depends(get_current_user), config=Depends(get_current_config)):
    return SettingsEdit(sampling_rate=config["litter"]["sampling_rate"]["value"],
                        use_counter=config["litter"]["use_counter"]["value"],
                        used_offset=config["litter"]["used_offset"]["value"],
                        tare_timeout=config["litter"]["tare_timeout"]["value"],
                        danger_threshold=config["litter"]["danger_threshold"]["value"],
                        danger_counter=config["litter"]["danger_counter"]["value"])


@router.put("/",
            summary="Update configuration",
            status_code=200, response_model=SettingsEdit)
def setting_update(*, data: SettingsEdit, current_user=Depends(get_current_user)):
    new = {
        "litter": {
            "sampling_rate": {
                "value": data.sampling_rate,
                "schema": "value in ms that determines the frequency in which measures are taken"
            },
            "use_counter": {
                "value": data.use_counter,
                "schema": "the number of consecutive readings that are enough to conclude that the litterbox is getting used by a pet"
            },
            "used_offset": {
                "value": data.used_offset,
                "schema": "the offset in weight that may trigger a 'litterbox in use' event (the minimum weight of the cat)"
            },
            "tare_timeout": {
                "value": data.tare_timeout,
                "schema": "the number of consecutive readings that need to be inside a certain tolerance to tare the device (since we want to remove used sand, this allows us to re-evaluate the amount of litter inside the litterbox)."
            },
            "danger_threshold": {
                "value": data.danger_threshold,
                "schema": "the threshold to generate the 'empty litterbox' alarm."
            },
            "danger_counter": {
                "value": data.danger_counter,
                "schema": "the number of consecutive 'empty litterbox' readings that will raise the alarm."
            }
        }
    }
    # TODO: Add MQTT request
    save_new_config(new)
    return data
