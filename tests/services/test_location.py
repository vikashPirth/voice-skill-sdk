#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

import respx
import pytest
from httpx import Response

from skill_sdk.services.location import LocationService, FullLocation, Address

SERVICE_URL = "http://service-location-service:1555/v1/location"
FORWARD_RESPONSE = {
    "lat": 49.87237,
    "lng": 8.65098,
    "timeZone": "Europe/Berlin",
    "address": {
        "country": "Deutschland",
        "addressComponents": {"city": "Darmstadt", "postalCode": "64283"},
    },
}
REVERSE_RESPONSE = {
    "country": "Deutschland",
    "addressComponents": {"city": "Darmstadt", "postalCode": "postalCode"},
}


@respx.mock
@pytest.mark.asyncio
async def test_forward_lookup():
    service = LocationService(SERVICE_URL)
    respx.get(f"{SERVICE_URL}/geo").mock(
        return_value=Response(200, json=FORWARD_RESPONSE)
    )

    response = await service.forward_lookup(city="Darmstadt")
    assert response == FullLocation(**FORWARD_RESPONSE)


@respx.mock
@pytest.mark.asyncio
async def test_reverse_lookup():
    service = LocationService(SERVICE_URL)
    respx.get(f"{SERVICE_URL}/reversegeo").mock(
        return_value=Response(200, json=REVERSE_RESPONSE)
    )

    response = await service.reverse_lookup(*(49.872840, 8.691840))
    assert response == Address(**REVERSE_RESPONSE)
