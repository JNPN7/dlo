#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

from fastapi import FastAPI, HTTPException, Request

from dlo.api.common.response.json_response import MsgSpecJSONResponse
from dlo.common.exception.errors import DloError

log = logging.getLogger(__name__)


def register_exception(app: FastAPI):
    """
    Register global exception handlers on the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance to register handlers on.
    """

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        Handle global HTTP exception.

        Args:
            request (Request): The incoming FastAPI request.
            exc (HTTPException): The HTTP exception raised.

        Returns:
            MsgSpecJSONResponse: A JSON response containing the error details.
        """
        content = exc.detail
        request.state.__request_http_exception__ = content

        log.error(content)

        return MsgSpecJSONResponse(
            status_code=exc.status_code,
            content=content,
            headers=exc.headers,
        )

    @app.exception_handler(DloError)
    async def custom_exception_handler(request: Request, exc: DloError):
        """
        Handle global custom exception derived from DloError.

        Args:
            request (Request): The incoming FastAPI request.
            exc (DloError): The custom exception raised.

        Returns:
            MsgSpecJSONResponse: A JSON response containing the error message.
        """
        content = exc.MESSAGE
        if exc.data is not None:
            content = exc.data

        request.state.__request_custom_exception__ = content

        log.error(content)

        return MsgSpecJSONResponse(
            status_code=exc.HTTP_CODE,
            content=content,
            background=exc.background,
        )
