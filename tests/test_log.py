#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

import json
import logging
from logging import makeLogRecord, INFO
from unittest.mock import patch
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

import pytest
from skill_sdk import config, log, init_app


@pytest.fixture
def app():
    app = init_app()

    @app.route("/test")
    async def index(*args):
        record = makeLogRecord(
            {
                "levelno": INFO,
                "levelname": "INFO",
            }
        )
        return JSONResponse(json.loads(log.CloudGELFFormatter().format(record)))

    @app.route("/log")
    async def index(*args):
        logger = logging.getLogger(__name__)
        logger.debug("Debug message")
        return JSONResponse("ok")

    yield app
    app.close()


@pytest.fixture
def client(app):
    return TestClient(app)


def test_log_record(client):
    resp = client.get(
        "/test",
        headers={
            "x-b3-traceid": "trace-id",
            "X-B3-SpanId": "span-id",
            "X-TenantId": "tenant-id",
        },
    )

    expected = ["trace-id", "span-id", "tenant-id"]
    assert [
        v for k, v in resp.json().items() if k in ("traceId", "spanId", "tenant")
    ] == expected


def test_user_log(client):

    with patch.object(logging.Logger, "_log") as mock_debug:
        client.get(
            "/log",
        )
        mock_debug.assert_not_called()

        client.get(
            "/log",
            headers={
                "x-user-debug-log": "1",
            },
        )
        mock_debug.assert_called_once_with(10, "Debug message", ())


def test_uvicorn_patched():
    from uvicorn.config import LOGGING_CONFIG

    log.setup_logging(logging.DEBUG, config.FormatType.GELF)
    assert LOGGING_CONFIG["formatters"]["access"]["()"].endswith("CloudGELFFormatter")
    assert LOGGING_CONFIG["loggers"]["uvicorn"]["level"] == logging.DEBUG
    assert LOGGING_CONFIG["loggers"]["uvicorn.error"]["level"] == logging.DEBUG
    assert LOGGING_CONFIG["loggers"]["uvicorn.access"]["level"] == logging.DEBUG

    log.setup_logging(logging.ERROR, config.FormatType.HUMAN)
    assert LOGGING_CONFIG["formatters"]["access"]["()"].endswith("AccessFormatter")
    assert LOGGING_CONFIG["loggers"]["uvicorn"]["level"] == logging.ERROR
    assert LOGGING_CONFIG["loggers"]["uvicorn.error"]["level"] == logging.ERROR
    assert LOGGING_CONFIG["loggers"]["uvicorn.access"]["level"] == logging.ERROR


def test_gunicorn_logger():
    from types import SimpleNamespace
    from skill_sdk.log import GunicornLogger, CloudGELFFormatter

    logger = GunicornLogger(SimpleNamespace(errorlog="-"))

    for handler in logger.error_log.handlers:
        assert isinstance(handler.formatter, CloudGELFFormatter)

    for handler in logger.access_log.handlers:
        assert isinstance(handler.formatter, CloudGELFFormatter)
