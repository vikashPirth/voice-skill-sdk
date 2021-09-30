#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

from skill_sdk.responses import (
    ask,
    ask_freetext,
    tell,
    Card,
    CardAction,
    AudioPlayer,
    Response,
    ResponseType,
)
from skill_sdk.responses.card import GENERIC_DEFAULT, CARD_VERSION
from skill_sdk.responses.task import ClientTask

import pytest


def test_init_text():
    simple_response = Response("abc123", ResponseType.TELL)
    assert simple_response.text == "abc123"
    assert simple_response.type == "TELL"


def test_init_full():
    c = Card(title_text="cardtitle", text="cardtext")
    card_response = Response(
        "abc123", ResponseType.TELL, card=c, result={"code": 22}
    )
    assert card_response.text == "abc123"
    assert card_response.type == "TELL"
    assert card_response.card.title_text == "cardtitle"
    assert card_response.result.data["code"] == 22
    assert card_response.push_notification is None


def test_init_bad_type():
    with pytest.raises(ValueError):
        Response("abc123", "TEL")


def test_dict_ask():
    ask_response = Response("abc123", ResponseType.ASK).dict()
    assert "abc123" == ask_response["text"]
    assert "ASK" == ask_response["type"]


def test_dict_simple():
    simple_response = Response("abc123", ResponseType.TELL).dict()
    assert "abc123" == simple_response["text"]
    assert "TELL" == simple_response["type"]
    assert "pushNotification" not in simple_response


def test_dict_card():
    c = Card(title_text="cardtitle", text="cardtext")
    card_response = Response(
        "abc123", ResponseType.TELL, card=c, result={"code": 22}
    ).dict()
    assert card_response["text"] == "abc123"
    assert card_response["type"] == "TELL"
    assert card_response["card"]["data"]["titleText"] == "cardtitle"
    assert card_response["result"]["data"]["code"] == 22


def test_response_with_card():
    card = Card(
        text="Text",
    ).with_action(item_text="Title", item_action=CardAction.INTERNAL_RESPONSE_TEXT)
    response = tell("Hola").with_card(card).dict()

    assert response == {
            "type": "TELL",
            "text": "Hola",
            "card": {
                "type": GENERIC_DEFAULT,
                "version": CARD_VERSION,
                "data": {
                    "text": "Text",
                    "listSections": [
                        {
                            "items": [
                                {
                                    "itemText": "Title",
                                    "itemAction": "internal://showResponseText",
                                }
                            ]
                        }
                    ],
                },
            },
        }


def test_response_with_command():
    response = tell("Hola").with_command(AudioPlayer.play_stream("URL")).dict()
    assert response == {
            "text": "Hola",
            "type": "TELL",
            "result": {
                "data": {
                    "use_kit": {
                        "kit_name": "audio_player",
                        "action": "play_stream",
                        "parameters": {"url": "URL"},
                    }
                },
                "local": True,
            },
        }


def test_response_with_session():
    response = ask("Hola?").with_session(
        attr1="attr-1",
        attr2="attr-2",
    )
    assert response.dict() == {
            "text": "Hola?",
            "type": "ASK",
            "session": {"attributes": {"attr1": "attr-1", "attr2": "attr-2"}},
        }
    with pytest.raises(ValueError):
        tell("Hola").with_session(
            attr1="attr-1",
            attr2="attr-2",
        )


def test_response_with_task():
    response = tell("Hola").with_task(ClientTask.invoke("WEATHER__INTENT"))
    assert response.dict() == {
            "type": "TELL",
            "text": "Hola",
            "result": {
                "data": {},
                "local": True,
                "delayedClientTask": {
                    "invokeData": {"intent": "WEATHER__INTENT", "parameters": {}},
                    "executionTime": {
                        "executeAfter": {
                            "reference": "SPEECH_END",
                            "offset": "P0D",
                        }
                    },
                },
            },
        }


def test_tell():
    r = tell("Hello")
    assert isinstance(r, Response)
    assert "TELL" == r.type


def test_ask():
    r = ask("Question")
    assert isinstance(r, Response)
    assert "ASK" == r.type


def test_ask_freetext():
    r = ask_freetext("Question")
    assert isinstance(r, Response)
    assert "ASK_FREETEXT" == r.type


def test_init_push_notification():
    simple_response = Response("abc123", ResponseType.TELL)
    response = simple_response.with_notification(
        target_name="device", message_payload="payload"
    ).dict()
    assert "abc123" == response["text"]
    assert "TELL" == response["type"]
    assert {"messagePayload": "payload", "targetName": "device"} == response["pushNotification"]


#
# TODO: double check if this functionality requested by skills, remove if not needed
#
"""
    def test_message(self):
    response = Response(Message('{abc}123', 'KEY', abc='abc')).dict()
    assert 'abc123' == response['text']
    assert ResponseType.TELL == response['type']
    assert {'key': 'KEY', 'value': '{abc}123', 'args': (), 'kwargs': {'abc': 'abc'}} == response['result']['data']
"""
