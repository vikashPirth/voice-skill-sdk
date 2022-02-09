#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

import json
import asyncio
import pathlib
import datetime
from datetime import date

from fastapi.testclient import TestClient

from skill_sdk import ui
from skill_sdk.utils import util
from skill_sdk.__version__ import __spi_version__


LOCALHOST = "http://localhost"


def test_list_intents_empty(app):
    r = TestClient(app).get("/intents")
    assert r.status_code == 200
    assert r.json() == []


def test_models(monkeypatch):
    param = ui.Parameter(**dict(name="Parameter", type="str", values=None))
    assert json.loads(param.json()) == {
        "name": "Parameter",
        "type": "str",
        "required": False,
        "sample": None,
        "values": [],
    }

    intent = ui.Intent(**dict(name="Intent"))
    assert json.loads(intent.json()) == {
        "name": "Intent",
        "implementation": ["impl", "handle_Intent"],
        "parameters": [],
    }

    def handle(i: int, t: str, f: float, dt: date):
        ...

    with util.mock_date_today(datetime.date(2100, 12, 31)):
        intent = ui.Intent.from_callable("Test_Intent", handle)
    assert json.loads(intent.json()) == {
        "name": "Test_Intent",
        "implementation": ["test_ui", "handle"],
        "parameters": [
            {"name": "i", "type": "int", "required": True, "sample": 42, "values": []},
            {
                "name": "t",
                "type": "str",
                "required": True,
                "sample": "string value",
                "values": [],
            },
            {
                "name": "f",
                "type": "float",
                "required": True,
                "sample": 42.0242,
                "values": [],
            },
            {
                "name": "dt",
                "type": "date",
                "required": True,
                "sample": "2100-12-31",
                "values": [],
            },
        ],
    }


def test_list_intents(app):
    @app.intent_handler("Test_Intent")
    def handle(i: int, t: str, f: float, dt: date):
        ...

    r = TestClient(app).get("/intents")
    assert r.status_code == 200
    assert r.json() == [
        {
            "name": "Test_Intent",
            "implementation": ["test_ui", "handle"],
            "parameters": [
                {
                    "name": "i",
                    "type": "int",
                    "required": True,
                    "sample": ui.samples("int"),
                    "values": [],
                },
                {
                    "name": "t",
                    "type": "str",
                    "required": True,
                    "sample": ui.samples("str"),
                    "values": [],
                },
                {
                    "name": "f",
                    "type": "float",
                    "required": True,
                    "sample": ui.samples("float"),
                    "values": [],
                },
                {
                    "name": "dt",
                    "type": "date",
                    "required": True,
                    "sample": str(ui.samples("date")),
                    "values": [],
                },
            ],
        }
    ]


def test_list_types(app):

    assert TestClient(app).get("/types").json() == [
        "bool",
        "int",
        "float",
        "complex",
        "str",
        "timedelta",
        "datetime",
        "date",
        "time",
        "TimeRange",
        "TimeSet",
        "AttributeV2",
        "typing.List[str]",
    ]


def test_worker_attach(mocker, app):

    # Workaround for Python 3.7 that has no AsyncMock
    worker_mock = mocker.patch.object(
        ui.notifier, "worker", return_value=asyncio.Future()
    )
    client = TestClient(app)
    with client:
        worker_mock.assert_called_once()

    with client:
        with client.websocket_connect("/logs") as websocket:
            # TODO:
            pass


def test_if_ui_generated():
    """Tests files existence, not real UI unit test"""

    ui_root = pathlib.Path(ui.__file__).parent
    required_files = [
        (ui_root / "index.html").exists(),
        len(list((ui_root / "css").glob("app.*.css"))) == 1,
        len(list((ui_root / "css").glob("chunk-vendors.*.css"))) == 1,
        len(list((ui_root / "js").glob("app.*.js"))) == 1,
        len(list((ui_root / "js").glob("chunk-vendors.*.js"))) == 1,
    ]
    assert all((_ for _ in required_files))


def test_spi_version():
    """SPI Version is hardcoded into the TestIntent.vue"""

    ui_root = pathlib.Path(ui.__file__).parent

    assert [
        js
        for js in (ui_root / "js").glob("app.*.js")
        if f'spiVersion:"{__spi_version__}"' in js.read_text()
    ] != []


def test_from_callable_with_list():
    from typing import List

    def handle_string(s: str):
        ...

    intent = ui.Intent.from_callable("Test_Intent", handle_string)
    assert (
        repr(intent) == "Intent(name='Test_Intent', "
        "implementation=('test_ui', 'handle_string'), "
        "parameters=[Parameter(name='s', type='str', required=True, sample='string value', values=[])])"
    )

    def handle_list(s: List[str]):
        ...

    intent = ui.Intent.from_callable("Test_Intent", handle_list)
    assert (
        repr(intent) == "Intent(name='Test_Intent', "
        "implementation=('test_ui', 'handle_list'), "
        "parameters=[Parameter(name='s', type='typing.List[str]', required=True, sample=['string value'], values=[])])"
    )
