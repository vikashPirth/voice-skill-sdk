#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

from collections import namedtuple
import unittest

from skill_sdk.responses import (
    AudioPlayer,
    Calendar,
    System,
    Timer,
)
from skill_sdk.responses.command import KitType


class TestKits(unittest.TestCase):
    def test_audio_player(self):
        command = AudioPlayer.play_stream("URL").dict()
        self.assertEqual(
            {
                "use_kit": {
                    "kit_name": "audio_player",
                    "action": "play_stream",
                    "parameters": {"url": "URL"},
                }
            },
            command,
        )

        command = AudioPlayer.play_stream_before_text("URL").dict()
        self.assertEqual(
            {
                "use_kit": {
                    "kit_name": "audio_player",
                    "action": "play_stream_before_text",
                    "parameters": {"url": "URL"},
                }
            },
            command,
        )

        command = AudioPlayer.stop(text="We're getting STOPPED!").dict()
        self.assertEqual(
            {
                "use_kit": {
                    "kit_name": "audio_player",
                    "action": "stop",
                    "parameters": {
                        "content_type": "radio",
                        "notify": {"not_playing": "We're getting STOPPED!"},
                    },
                }
            },
            command,
        )

        command = AudioPlayer.pause(text="We're PAUSED!").dict()
        self.assertEqual(
            {
                "use_kit": {
                    "kit_name": "audio_player",
                    "action": "pause",
                    "parameters": {
                        "content_type": "radio",
                        "notify": {"not_playing": "We're PAUSED!"},
                    },
                }
            },
            command,
        )

        command = AudioPlayer.resume("voicemail").dict()
        self.assertEqual(
            {
                "use_kit": {
                    "kit_name": "audio_player",
                    "action": "resume",
                    "parameters": {"content_type": "voicemail"},
                }
            },
            command,
        )

    def test_calendar(self):
        command = Calendar.snooze_start(5).dict()
        self.assertEqual(
            {
                "use_kit": {
                    "kit_name": "calendar",
                    "action": "snooze_start",
                    "parameters": {"snooze_seconds": 5},
                }
            },
            command,
        )

        command = Calendar.snooze_cancel().dict()
        self.assertEqual(
            {"use_kit": {"kit_name": "calendar", "action": "snooze_cancel"}}, command
        )

    def test_timer(self):
        command = Timer.set_timer().dict()
        self.assertEqual(
            {"use_kit": {"kit_name": "timer", "action": "set_timer"}}, command
        )

        command = Timer.cancel_timer().dict()
        self.assertEqual(
            {"use_kit": {"kit_name": "timer", "action": "cancel_timer"}}, command
        )

    def test_system(self):
        command = System.stop("Media").dict()
        self.assertEqual(
            {
                "use_kit": {
                    "kit_name": "system",
                    "action": "stop",
                    "parameters": {"skill": "Media"},
                }
            },
            command,
        )

        for action in System.Action:
            if action not in ("stop", "volume_to"):
                command = getattr(System, action)().dict()
                self.assertEqual(
                    {"use_kit": {"kit_name": "system", "action": action}}, command
                )

        command = System.volume_to(5).dict()
        self.assertEqual(
            {
                "use_kit": {
                    "kit_name": "system",
                    "action": "volume_to",
                    "parameters": {"value": 5},
                }
            },
            command,
        )
        with self.assertRaises(ValueError):
            System.volume_to(12)
