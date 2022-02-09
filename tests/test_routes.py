#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

from base64 import b64encode
import pytest

from fastapi.testclient import TestClient

from skill_sdk.config import settings
from skill_sdk.responses import command, ask, tell
from skill_sdk.utils.util import create_request
from skill_sdk.skill import init_app, FALLBACK_INTENT
from skill_sdk.__version__ import __version__, __spi_version__


ENDPOINT = "/v1/skill-noname"
SKILL_INFO = {
    "skillId": "skill-noname",
    "skillVersion": f"1 {__version__}",
    "supportedLocales": [],
    "skillSpiVersion": __spi_version__,
}


@pytest.fixture
def app():
    app = init_app()
    yield app
    app.close()


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def auth_header():
    credentials = b64encode(
        ":".join((settings.SKILL_API_USER, settings.SKILL_API_KEY)).encode()
    ).decode("ascii")
    return {"Authorization": f"Basic {credentials}"}


def test_health(app, client):
    response = client.get(settings.K8S_READINESS)
    assert response.status_code == 418
    assert response.json() == {"text": "No intent handlers loaded!"}

    app.include("Test_Intent", handler=lambda: "Hola")
    response = client.get(settings.K8S_READINESS)
    assert response.status_code == 200


def test_info_response(client, auth_header):
    response = client.get(
        "/v1/skill-noname/info",
        headers=auth_header,
    )
    assert response.status_code == 200
    assert response.json() == SKILL_INFO


def test_invoke_intent_not_found(client, auth_header):
    response = client.post(
        ENDPOINT,
        json=create_request("Test_Intent").dict(),
        headers=auth_header,
    )
    assert response.status_code == 404
    assert response.json() == {"code": 1, "text": "Intent not found!"}


def test_invoke_fallback_intent(app, client, auth_header):
    app.include(FALLBACK_INTENT, handler=lambda: "Hello fallback")
    response = client.post(
        ENDPOINT,
        json=create_request("Test_Intent").dict(),
        headers=auth_header,
    )
    assert response.status_code == 200
    assert response.json() == {"text": "Hello fallback", "type": "TELL"}


def test_invoke_response_tell(app, client, auth_header):
    def handler():
        from skill_sdk.intents.request import r

        r.session["Session Key"] = "Hola"
        return "Hola"

    app.include("Test_Intent", handler=handler)

    response = client.post(
        ENDPOINT,
        json=create_request("Test_Intent", session={}).dict(),
        headers=auth_header,
    )
    assert response.status_code == 200
    assert response.json() == {"text": "Hola", "type": "TELL"}


def test_invoke_response_ask(app, client, auth_header):
    def handler():
        from skill_sdk.intents.request import r

        r.session["Session Key"] = "Hello"
        return ask("Hello?")

    app.include("Test_Intent", handler=handler)

    response = client.post(
        ENDPOINT,
        json=create_request("Test_Intent", session={}).dict(),
        headers=auth_header,
    )
    assert response.status_code == 200
    assert response.json() == {
        "text": "Hello?",
        "type": "ASK",
        "session": {"attributes": {"Session Key": "Hello"}},
    }


def test_root_redirect(client):
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/redoc"


def test_response_with_card_and_command(app, client, auth_header):
    from skill_sdk.responses.card import Card

    app.include(
        "Test_Intent",
        handler=lambda: (
            tell("Hola")
            .with_card(
                Card(title_text="Test").with_action(
                    item_text="Text", item_action="action"
                )
            )
            .with_command(command.AudioPlayer.play_stream("kool url"))
        ),
    )

    response = client.post(
        ENDPOINT,
        json=create_request("Test_Intent", session={}).dict(),
        headers=auth_header,
    )
    assert response.status_code == 200
    assert response.json() == {
        "text": "Hola",
        "type": "TELL",
        "card": {
            "type": "GENERIC_DEFAULT",
            "version": 3,
            "data": {
                "titleText": "Test",
                "listSections": [
                    {"items": [{"itemText": "Text", "itemAction": "action"}]}
                ],
            },
        },
        "result": {
            "data": {
                "use_kit": {
                    "kit_name": "audio_player",
                    "action": "play_stream",
                    "parameters": {"url": "kool url"},
                }
            },
            "local": True,
        },
    }
