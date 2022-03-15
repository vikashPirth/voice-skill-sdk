#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

from skill_sdk.responses import Response, Reprompt, ResponseType

from skill_sdk.intents import request


def test_reprompt_response(monkeypatch):
    from skill_sdk.utils.util import test_request

    with test_request("SMALLTALK__GREETINGS"):
        response = Reprompt("abc123")
        assert isinstance(response, Response)

        response_dict = response.dict()
        assert response_dict["text"] == "abc123"
        assert response_dict["type"] == ResponseType.ASK
        assert request.session["SMALLTALK__GREETINGS_reprompt_count"] == 1

        response_dict = Reprompt("abc123").dict()
        assert response_dict["text"] == "abc123"
        assert response_dict["type"] == ResponseType.ASK
        assert request.session["SMALLTALK__GREETINGS_reprompt_count"] == 2

        response_dict = Reprompt("abc123", "321cba", 2).dict()
        assert response_dict["text"] == "321cba"
        assert response_dict["type"] == ResponseType.TELL
        assert "SMALLTALK_GREETINGS_reprompt_count" not in request.session

        monkeypatch.setitem(
            request.session.attributes,
            "SMALLTALK__GREETINGS_reprompt_count",
            "not a number",
        )
        Reprompt("abc123").dict()
        assert request.session["SMALLTALK__GREETINGS_reprompt_count"] == 1

        Reprompt("abc123", entity="Time").dict()
        assert request.session["SMALLTALK__GREETINGS_Time_reprompt_count"] == 1

        attributes = request.session.attributes
        assert attributes["SMALLTALK__GREETINGS_reprompt_count"] == 1
        assert attributes["SMALLTALK__GREETINGS_Time_reprompt_count"] == 1
