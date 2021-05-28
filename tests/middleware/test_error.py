#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from skill_sdk.middleware.error import (
    ErrorCode,
    BAD_REQUEST,
    INTERNAL_ERROR,
    NOT_FOUND,
    setup_middleware,
)


@pytest.fixture
def app():
    app = FastAPI(debug=True)
    setup_middleware(app)
    return app


def test_422(app):
    @app.get("/validation/{param}/")
    def validation_exception(param: int):
        pass  # noqa

    client = TestClient(app)
    response = client.get("/validation/not-int/")
    assert response.status_code == 422
    assert response.json() == dict(
        code=ErrorCode.BAD_REQUEST,
        text=BAD_REQUEST,
        detail=[
            {
                "loc": ["path", "param"],
                "msg": "value is not a valid integer",
                "type": "type_error.integer",
            }
        ],
    )


def test_404(app):
    client = TestClient(app)
    response = client.get("/http-404")
    assert response.status_code == 404
    assert response.json() == dict(code=ErrorCode.NOT_FOUND, text=NOT_FOUND)


def test_500(app):

    # If debug is enabled and an error occurs,
    # then instead of using the installed 500 handler,
    # Starlette will respond with a traceback response.
    app.debug = False

    @app.get("/http-500")
    def exception():
        raise RuntimeError("Does not work")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/http-500")
    assert response.status_code == 500
    assert response.json() == dict(code=ErrorCode.INTERNAL_ERROR, text=INTERNAL_ERROR)
