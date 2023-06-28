from datetime import datetime
from uuid import UUID
import typing as t
from data_proxy.backend.web.models import edit, base

__all__ = (
    "UserRead"
)


class UserRead(base.Model):
    username: str
