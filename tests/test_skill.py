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

from fastapi.testclient import TestClient
from skill_sdk import skill, ResponseType


@pytest.fixture
def app():
    app = skill.init_app()
    yield app
    app.close()


def test_intent_handlers(app):
    assert app.intents == {}
    app.include("Test_Intent", handler=lambda: "Hola")

    with pytest.raises(ValueError):
        # Cannot redefine existing intent...
        app.include("Test_Intent", handler=lambda: "Hola")

    with pytest.raises(ValueError):
        # Duplicate intent
        @app.intent_handler("Test_Intent")
        def handler():
            ...

    with pytest.raises(ValueError):
        # Wrong handler type...
        app.include("Another_Test_Intent", handler="Hola")  # noqa


@pytest.mark.asyncio
async def test_with_error_handler(app):
    def error_handler(name, exc):
        return str(exc.__cause__)

    def handler(number: int):
        return int(number)

    app.include(
        "Another_Test_Intent", handler=handler, error_handler=error_handler  # noqa
    )
    result = await app.test_intent("Another_Test_Intent", number="str")
    assert result.text == "invalid literal for int() with base 10: 'str'"


@pytest.mark.asyncio
async def test_test_intent_async(app):
    with pytest.raises(KeyError):
        await app.test_intent("Test_Intent")

    app.include("Test_Intent", handler=lambda: "Hola")
    result = await app.test_intent("Test_Intent")

    assert result.text == "Hola"
    assert result.type == ResponseType.TELL


def test_test_intent_sync(app):
    app.include("Test_Intent", handler=lambda: "Hola")
    result = skill.test_intent("Test_Intent")

    assert result.text == "Hola"
    assert result.type == ResponseType.TELL


def test_technical_endpoints(app):
    from skill_sdk.config import settings

    app.include("Test_Intent", handler=lambda: "Hola")
    client = TestClient(app)

    # Kubernetes "readiness"
    assert client.get(settings.K8S_READINESS).status_code == 200

    # Kubernetes "liveness"
    assert client.get(settings.K8S_LIVENESS).status_code == 200

    # Prometheus scraper
    prometheus = getattr(settings, "PROMETHEUS_ENDPOINT", "/prometheus")
    assert client.get(prometheus).status_code == 200
