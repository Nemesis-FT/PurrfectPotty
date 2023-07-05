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
    danger_threshold: int
    danger_counter: int
