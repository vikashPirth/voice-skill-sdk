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
from impl.hello import handler


@pytest.mark.asyncio
async def test_hello_response():
    response = await skill.test_intent("SMALLTALK__GREETINGS")
    assert response.text == "HELLOAPP_HELLO"
