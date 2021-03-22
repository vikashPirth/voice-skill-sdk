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

from skill_sdk.responses.task import ClientTask


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


