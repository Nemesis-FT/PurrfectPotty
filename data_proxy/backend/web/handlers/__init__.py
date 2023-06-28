import typing as t

import fastapi

from data_proxy.backend.web import errors


# noinspection PyUnusedLocal
async def handle_application_error(request: fastapi.Request, exc: errors.ApplicationException) -> fastapi.Response:
    return exc.to_response()


# noinspection PyUnusedLocal
async def handle_generic_error(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    raise errors.ApplicationException()
