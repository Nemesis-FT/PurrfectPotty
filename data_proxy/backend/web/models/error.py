from data_proxy.backend.web.models import base

__all__ = (
    "ErrorModel",
)


class ErrorModel(base.Model):
    """
    Model for errors returned by the API.
    """

    error_code: str
    reason: str

    class Config(base.Model.Config):
        schema_extra = {
            "example": {
                "error_code": "NOT_FOUND",
                "reason": "The requested object was not found.",
            },
        }
