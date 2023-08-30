import typing as t
import pydantic
from uuid import UUID
from data_proxy.backend.web.models import base
import datetime

__all__ = (
    "SettingEdit"
)


class SettingsEdit(base.Model):
    sampling_rate: int
    use_counter: int
    used_offset: int
    tare_timeout: int


class ActionEdit(base.Model):
    thing_token: str
    timestamp: str


class TempAction(ActionEdit):
    temperature: str


class RssiAction(ActionEdit):
    rssi_str: int


class LitterUsed(ActionEdit):
    pass


class LitterEmpty(ActionEdit):
    pass