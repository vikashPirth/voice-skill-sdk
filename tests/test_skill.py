#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

from contextlib import closing
import pytest

from skill_sdk import skill, ResponseType


def test_intent_handlers():
    app = skill.init_app()

    with closing(app):

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
async def test_with_error_handler():
    app = skill.init_app()

    with closing(app):

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
async def test_test_intent_async():
    app = skill.init_app()

    with closing(app):
        with pytest.raises(KeyError):
            await app.test_intent("Test_Intent")

        app.include("Test_Intent", handler=lambda: "Hola")
        result = await app.test_intent("Test_Intent")

        assert result.text == "Hola"
        assert result.type == ResponseType.TELL


def test_sync_test_intent():
    app = skill.init_app()

    with closing(app):

        app.include("Test_Intent", handler=lambda: "Hola")
        result = skill.test_intent("Test_Intent")

        assert result.text == "Hola"
        assert result.type == ResponseType.TELL
