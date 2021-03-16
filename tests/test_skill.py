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
            app.include("Test_Intent", handler=lambda: "Hola")

        with pytest.raises(ValueError):
            # Duplicate intent
            @app.intent_handler("Test_Intent")
            def handler():
                ...

        with pytest.raises(ValueError):
            app.include("Test_Intent", handler="Hola")  # noqa

        @app.intent_handler
        def handler():
            ...

        assert handler.__intent_handler__ is True


@pytest.mark.asyncio
async def test_test_intent():
    app = skill.init_app()

    with closing(app):
        with pytest.raises(KeyError):
            await app.test_intent("Test_Intent")

        app.include("Test_Intent", handler=lambda: "Hola")
        result = await app.test_intent("Test_Intent")

        assert result.text == "Hola"
        assert result.type == ResponseType.TELL
