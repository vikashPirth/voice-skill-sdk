#
# voice-skill-sdk
#
# (C) 2021, YOUR_NAME (YOUR COMPANY), Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

import pytest
from skill_sdk import skill
from impl import hello


@pytest.fixture
def app():
    app = skill.init_app()
    app.include(handler=hello.handler)
    return app


@pytest.mark.asyncio
async def test_intent_async(app):
    response = await app.test_intent("SMALLTALK__GREETINGS")
    assert response.text == "HELLOAPP_HELLO"


def test_intent_sync(app):
    response = skill.test_intent("SMALLTALK__GREETINGS")
    assert response.text == "HELLOAPP_HELLO"
