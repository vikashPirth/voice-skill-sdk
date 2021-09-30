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

from skill_sdk.responses import (
    AudioPlayer,
    Calendar,
    System,
    Timer,
)


def test_audio_player():
    command = AudioPlayer.play_stream("URL").dict()
    assert command == {
            "use_kit": {
                "kit_name": "audio_player",
                "action": "play_stream",
                "parameters": {"url": "URL"},
            }
        }

    command = AudioPlayer.play_stream_before_text("URL").dict()
    assert command == {
            "use_kit": {
                "kit_name": "audio_player",
                "action": "play_stream_before_text",
                "parameters": {"url": "URL"},
            }
        }


    command = AudioPlayer.stop(text="We're getting STOPPED!").dict()
    assert command == {
            "use_kit": {
                "kit_name": "audio_player",
                "action": "stop",
                "parameters": {
                    "content_type": "radio",
                    "notify": {"not_playing": "We're getting STOPPED!"},
                },
            }
        }

    command = AudioPlayer.pause(text="We're PAUSED!").dict()
    assert command =={
            "use_kit": {
                "kit_name": "audio_player",
                "action": "pause",
                "parameters": {
                    "content_type": "radio",
                    "notify": {"not_playing": "We're PAUSED!"},
                },
            }
        }

    command = AudioPlayer.resume("voicemail").dict()
    assert command == {
            "use_kit": {
                "kit_name": "audio_player",
                "action": "resume",
                "parameters": {"content_type": "voicemail"},
            }
        }


def test_calendar():
    command = Calendar.snooze_start(5).dict()
    assert command == {
            "use_kit": {
                "kit_name": "calendar",
                "action": "snooze_start",
                "parameters": {"snooze_seconds": 5},
            }
        }

    command = Calendar.snooze_cancel().dict()
    assert command == {"use_kit": {"kit_name": "calendar", "action": "snooze_cancel"}}


def test_timer():
    command = Timer.set_timer().dict()
    assert command == {"use_kit": {"kit_name": "timer", "action": "set_timer"}}

    command = Timer.cancel_timer().dict()
    assert command == {"use_kit": {"kit_name": "timer", "action": "cancel_timer"}}


def test_system():
    command = System.stop("Media").dict()
    assert command == {
            "use_kit": {
                "kit_name": "system",
                "action": "stop",
                "parameters": {"skill": "Media"},
            }
        }

    for action in System.Action:
        if action not in ("stop", "volume_to"):
            command = getattr(System, action)().dict()
            assert command == {"use_kit": {"kit_name": "system", "action": action}}

    command = System.volume_to(5).dict()
    assert command == {
            "use_kit": {
                "kit_name": "system",
                "action": "volume_to",
                "parameters": {"value": 5},
            }
        }
    with pytest.raises(ValueError):
        System.volume_to(12)
