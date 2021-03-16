#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

import json
import logging

import respx
from httpx import HTTPError, Response
import pytest
from skill_sdk.services.persistence import PersistenceService

PERSISTENCE_URL = "http://service-persistence-service:1555/v1/persistence"
ENTRY = "/entry"
DATA = "/entry/data"

allSkillData = """
{
    "data": {
        "attrs": {
            "attr1": "value1",
            "attr2": "value2"
        }
    }
}
"""

skillData = """
{
    "attrs": {
        "attr1": "value1",
        "attr2": "value2"
    }
}
"""

setResponse = """
{
    "id": "5c49c430bd35a20001438a7c",
    "data": {
        "attrs": {
            "attr1": "value1",
            "attr2": "value2"
        }
    }
}
"""

logger = logging.getLogger()


@respx.mock
@pytest.mark.asyncio
async def test_persistence_get():
    respx.get(PERSISTENCE_URL + DATA).mock(return_value=Response(200, text=skillData))

    service = PersistenceService(PERSISTENCE_URL)
    result = await service.get()
    assert result == {"attrs": {"attr1": "value1", "attr2": "value2"}}


@respx.mock
@pytest.mark.asyncio
async def test_persistence_get_invalid_data():
    respx.get(PERSISTENCE_URL + DATA).mock(
        return_value=Response(200, text=skillData[:50])
    )

    service = PersistenceService(PERSISTENCE_URL)
    with pytest.raises(json.JSONDecodeError):
        await service.get()


@respx.mock
@pytest.mark.asyncio
async def test_persistence_get_not_authorized():
    respx.get(PERSISTENCE_URL + DATA).mock(
        return_value=Response(401, text="Not Authorized")
    )

    service = PersistenceService(PERSISTENCE_URL)
    with pytest.raises(HTTPError):
        await service.get()


@respx.mock
@pytest.mark.asyncio
async def test_persistence_get_all():
    respx.get(PERSISTENCE_URL + ENTRY).mock(
        return_value=Response(200, text=allSkillData)
    )

    service = PersistenceService(PERSISTENCE_URL)
    result = await service.get_all()
    assert result == {"data": {"attrs": {"attr1": "value1", "attr2": "value2"}}}


@respx.mock
@pytest.mark.asyncio
async def test_persistence_set():
    respx.post(PERSISTENCE_URL + ENTRY).mock(
        return_value=Response(200, text=setResponse)
    )

    service = PersistenceService(PERSISTENCE_URL)
    result = await service.set(json.loads(skillData))
    assert result.json() == json.loads(setResponse)


@respx.mock
@pytest.mark.asyncio
async def test_persistence_delete():
    respx.delete(PERSISTENCE_URL + ENTRY).mock(return_value=Response(200, text="[]"))

    service = PersistenceService(PERSISTENCE_URL)
    result = await service.delete()
    assert isinstance(result, Response)
