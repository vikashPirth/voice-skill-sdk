#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

import asyncio
from datetime import date
from fastapi.testclient import TestClient

from skill_sdk.skill import init_app
from skill_sdk import ui


LOCALHOST = "http://localhost"


def test_client():
    app = init_app(develop=True)
    return TestClient(app)


def test_list_intents_empty():
    r = test_client().get("/intents")
    assert r.status_code == 200
    assert r.json() == []


def test_list_intents():
    client = test_client()

    @client.app.intent_handler("Test_Intent")
    def handle(i: int, t: str, f: float, dt: date):
        ...

    r = client.get("/intents")
    assert r.status_code == 200
    assert r.json() == [
        {
            "name": "Test_Intent",
            "implementation": "handle",
            "parameters": [
                {
                    "name": "i",
                    "type": "<class 'int'>",
                    "required": True,
                    "sample": ui.SAMPLES[int],
                    "values": [],
                },
                {
                    "name": "t",
                    "type": "<class 'str'>",
                    "required": True,
                    "sample": ui.SAMPLES[str],
                    "values": [],
                },
                {
                    "name": "f",
                    "type": "<class 'float'>",
                    "required": True,
                    "sample": ui.SAMPLES[float],
                    "values": [],
                },
                {
                    "name": "dt",
                    "type": "<class 'datetime.date'>",
                    "required": True,
                    "sample": str(ui.SAMPLES[date]),
                    "values": [],
                },
            ],
        }
    ]


def test_worker_attach(mocker):
    client = test_client()

    # Workaround for Python 3.7 that has no AsyncMock
    worker_mock = mocker.patch.object(
        ui.notifier, "worker", return_value=asyncio.Future()
    )
    with client:
        worker_mock.assert_called_once()

    with client:
        with client.websocket_connect("/logs") as websocket:
            # TODO:
            pass
