#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

import datetime
import unittest
import pytest

from fastapi.testclient import TestClient
from skill_sdk import Response
from skill_sdk.util import Server, create_request
from skill_sdk.responses.task import ClientTask
from skill_sdk.skill import intent_handler, Skill


class TestTasks(unittest.TestCase):
    def test_response_tasks(self):

        task = ClientTask.invoke("WEATHER__INTENT", location="Berlin")
        self.assertEqual(
            {
                "invokeData": {
                    "intent": "WEATHER__INTENT",
                    "parameters": {"location": "Berlin"},
                },
                "executionTime": {
                    "executeAfter": {"reference": "SPEECH_END", "offset": "P0D"}
                },
            },
            task.dict(),
        )

        task = task.after(offset=datetime.timedelta(seconds=10))
        self.assertEqual(
            {
                "invokeData": {
                    "intent": "WEATHER__INTENT",
                    "parameters": {"location": "Berlin"},
                },
                "executionTime": {
                    "executeAfter": {"reference": "SPEECH_END", "offset": "PT10S"}
                },
            },
            task.dict(),
        )

        task = task.at(datetime.datetime(year=2120, month=12, day=31))
        self.assertEqual(
            {
                "invokeData": {
                    "intent": "WEATHER__INTENT",
                    "parameters": {"location": "Berlin"},
                },
                "executionTime": {"executeAt": "2120-12-31T00:00:00"},
            },
            task.dict(),
        )


def test_response_with_delayed_task(app: Skill):
    @intent_handler
    def response_with_task():
        from skill_sdk.i18n import _

        return Response(_("Hola")).with_task(
            ClientTask.invoke("HOLA_INTENT", skill_id="skill-id").after(
                offset=datetime.timedelta(seconds=10)
            )
        )

    app.include("TEST_HOLA", handler=response_with_task)
    client = TestClient(app)

    with Server(app).run_in_thread():
        result = client.post(
            "/v1/skill-noname", data=create_request("TEST_HOLA").json()
        )
        assert result.json() == {
            "text": "Hola",
            "type": "TELL",
            "result": {
                "data": {},
                "local": True,
                "delayedClientTask": {
                    "invokeData": {
                        "intent": "HOLA_INTENT",
                        "skillId": "skill-id",
                        "parameters": {},
                    },
                    "executionTime": {
                        "executeAfter": {"reference": "SPEECH_END", "offset": "PT10S"}
                    },
                },
            },
        }
