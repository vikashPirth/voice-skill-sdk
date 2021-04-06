#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

"""Skill Desinger UI"""

import asyncio
import inspect
from json import dumps
import logging.handlers
from pathlib import Path
from typing import Any, Callable, List, Optional, Text, Type
import datetime
from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from skill_sdk.util import CamelModel
from skill_sdk.intents.entities import AttributeV2

logger = logging.getLogger()

UI_ROOT = Path(__file__).absolute().parent

#
#   Sample values for intent handlers
#

SAMPLE_INT = 42
SAMPLE_FLOAT = 42.0242
SAMPLE_STRING = "string value"
SAMPLE_ATTR_V2: AttributeV2 = AttributeV2(id=1, value=SAMPLE_STRING)

SAMPLES = {
    int: SAMPLE_INT,
    float: SAMPLE_FLOAT,
    str: SAMPLE_STRING,
    datetime.timedelta: datetime.timedelta(),
    datetime.datetime: datetime.datetime.now(),
    datetime.date: datetime.date.today(),
    datetime.time: datetime.datetime.now().time(),
    AttributeV2: SAMPLE_ATTR_V2,
    List[str]: [SAMPLE_STRING],
}


# TODO: entities.TimeRange/TimeSet


class Parameter(CamelModel):
    """Parameter record format"""

    # Parameter name
    name: Text

    # Parameter type
    type: Text

    # Required if non-empty and has no default
    required: bool

    # Sample value
    sample: Any

    # Values array
    values: List[Optional[Any]]

    def __init__(self, name: Text, type_: Type, default: Any = None):
        required, values = False, []
        sample = SAMPLES.get(type_, None)

        if default == inspect.Parameter.empty:
            required = True
        elif default is not None:
            values = [default]

        super().__init__(
            name=name, type=str(type_), required=required, sample=sample, values=values
        )


class Intent(CamelModel):
    """Intent record format"""

    # Intent name
    name: Text

    # Implementation name
    implementation: Text

    # List of intent handler parameters (entities)
    parameters: List[Parameter]

    def __init__(self, name: Text, func: Callable):
        implementation = func.__name__

        __params = inspect.signature(func).parameters
        parameters = [
            Parameter(
                p_name,
                param.annotation,
                param.default,
            )
            for p_name, param in __params.items()
        ]

        super().__init__(
            name=name, implementation=implementation, parameters=parameters
        )


async def get_intents(request: Request):
    """
    List intents and entity samples
    """

    return [Intent(name, func) for name, func in request.app.intents.items()]


class Notifier:
    """Notifies subscribed clients"""

    def __init__(self):
        self.connections: List[WebSocket] = []
        self.generator = self.get_notification_generator()

    async def get_notification_generator(self):
        while True:
            message = yield
            await self._notify(message)

    async def push(self, msg: Text):
        await self.generator.asend(msg)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def remove(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def _notify(self, message: Text):
        living_connections = []
        while len(self.connections) > 0:
            # Looping is necessary in case a disconnection is handled
            # during await websocket.send_text(message)
            websocket = self.connections.pop()
            await websocket.send_text(message)
            living_connections.append(websocket)
        self.connections = living_connections

    async def worker(self, queue):
        """
        Async worker: waits for a log record and sends to subscribed clients

        :param queue:
        :return:
        """
        while True:
            record: logging.LogRecord = await queue.get()
            await self.push(dumps(record.__dict__))


notifier = Notifier()


async def ws_endpoint(websocket: WebSocket):
    """
    Dump logs output to websocket

    :param websocket:
    :return:
    """
    await notifier.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        try:
            notifier.remove(websocket)
        except ValueError:
            pass  # Shutting down (?)


def setup(app: FastAPI):
    """
    Install skill designer UI routes and CORS middleware

    :param app:
    :return:
    """

    # CORS middleware to allow requests from dev and prod UI
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8080",
            "http://127.0.0.1:8080",
            "http://localhost:4242",
            "http://127.0.0.1:4242",
        ],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # List intents route
    app.add_api_route(
        "/intents",
        get_intents,
        name="Designer UI",
        tags=["Designer endpoints"],
    )

    # Websocket logs push
    app.add_websocket_route(
        "/logs",
        ws_endpoint,
        name="Skill Logs",
    )

    @app.on_event("startup")
    async def startup():
        """Initializes websocket listener"""

        # Prime the push notification generator
        await notifier.generator.asend(None)

        # Silence the websocket.protocol logger
        logging.getLogger("websockets").setLevel(logging.CRITICAL)

        # Setup a queue that passes log records to websockets
        queue = asyncio.Queue()

        # Default format of the log record in front-end
        formatter = logging.Formatter("%(levelname)-8s %(name)s - %(message)s")

        handler = logging.handlers.QueueHandler(queue)
        handler.setLevel(logger.level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Start the notifier's worker
        asyncio.ensure_future(notifier.worker(queue))

    # Root UI
    app.mount("/", StaticFiles(directory=str(UI_ROOT), html=True), name="Skill UI")
