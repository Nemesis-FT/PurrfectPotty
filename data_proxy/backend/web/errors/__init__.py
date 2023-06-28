"""
This module contains the possible errors that can be raised by :mod:`impressive_strawberry`, and then possibly be caught by one of the :mod:`impressive_strawberry.handlers`.
"""

import fastapi

from data_proxy.backend.web import models

__all__ = (
    "ApplicationException",
    "MissingAuthHeader",
    "InvalidAuthHeader",
    "WrongAuthHeader",
    "ResourceNotFound",
    "MultipleResultsFound",
    "EntityAlreadyExists",
    "Denied"
)


class ApplicationException(Exception):
    """
    Base class for :mod:`impressive_strawberry` exceptions.
    """

    STATUS_CODE: int = 500
    ERROR_CODE: str = "UNKNOWN"
    REASON: str = "Unknown error."

    @classmethod
    def to_model(cls) -> models.error.ErrorModel:
        return models.error.ErrorModel(error_code=cls.ERROR_CODE, reason=cls.REASON)

    @classmethod
    def to_response(cls) -> fastapi.Response:
        return fastapi.Response(content=cls.to_model().json(), status_code=cls.STATUS_CODE,
                                media_type="application/json")


class MissingAuthHeader(ApplicationException):
    STATUS_CODE = 401
    ERROR_CODE = "MISSING_AUTH_HEADER"
    REASON = "The Authorization header is missing."


class InvalidAuthHeader(ApplicationException):
    STATUS_CODE = 401
    ERROR_CODE = "INVALID_AUTH_HEADER"
    REASON = "The provided Authorization header is invalid."


class WrongAuthHeader(ApplicationException):
    STATUS_CODE = 401
    ERROR_CODE = "WRONG_AUTH_HEADER"
    REASON = "The value provideed in the Authorization header is in a valid format, but its value is incorrect."


class ResourceNotFound(ApplicationException):
    STATUS_CODE = 404
    ERROR_CODE = "NOT_FOUND"
    REASON = "The requested resource was not found. Either it does not exist, or you are not authorized to view it."


class MultipleResultsFound(ApplicationException):
    STATUS_CODE = 500
    ERROR_CODE = "MULTIPLE_FOUND"
    REASON = "Multiple resources were found with the requested identifier."


class EntityAlreadyExists(ApplicationException):
    STATUS_CODE = 500
    ERROR_CODE = "ALREADY_EXISTS"
    REASON = "Another Entity already exists with the same unique values."


class Denied(ApplicationException):
    STATUS_CODE = 403
    ERROR_CODE = "DENIED"
    REASON = "You lack the authority to attempt this action."
