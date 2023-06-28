from __future__ import annotations

import abc
import datetime
import uuid
import pydantic


__all__ = (
    "Model",
    "ORMModel",
)


class Model(pydantic.BaseModel, metaclass=abc.ABCMeta):
    """
    Base model for :mod:`codex`\\ 's :mod:`pydantic` models.
    """

    class Config(pydantic.BaseModel.Config):
        json_encoders = {
            uuid.UUID:
                lambda obj: str(obj),
            datetime.datetime:
                lambda obj: obj.timestamp(),
            datetime.date:
                lambda obj: obj.isoformat(),
        }


class ORMModel(Model, metaclass=abc.ABCMeta):
    """
    Extension to :class:`.Model` which enables the :attr:`.Model.Config.orm_mode`.
    """

    class Config(Model.Config):
        orm_mode = True
