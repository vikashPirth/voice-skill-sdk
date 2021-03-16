#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

#
# Geolocation service
#

import logging
from typing import Optional, Text

from skill_sdk.util import CamelModel
from skill_sdk.services.base import BaseService

logger = logging.getLogger(__name__)


class GeoLocation(CamelModel):

    lat: float
    lng: float


class AddressComponents(CamelModel):

    city: Text
    postal_code: Text


class Address(CamelModel):

    country: Text
    address_components: AddressComponents


class Location(CamelModel):

    address: Address
    timezone: Text = "Europe/Berlin"


class FullLocation(GeoLocation, Location):
    ...


class GeoLookupQuery(CamelModel):

    country: Optional[Text]
    city: Optional[Text]
    postalcode: Optional[Text]  # noqa

    lang: Optional[Text]


class LocationService(BaseService):
    """Location service with geo-coding"""

    VERSION = 1
    NAME = "location"

    async def forward_lookup(
        self,
        *,
        country: Text = None,
        city: Text = None,
        postalcode: Text = None,  # noqa
        lang: Text = None,
    ) -> FullLocation:

        async with self.async_client as client:
            params = GeoLookupQuery(
                country=country, city=city, postalcode=postalcode, lang=lang
            )

            data = await client.get(f"{self.url}/geo", params=params.dict())
            return FullLocation(**data.json())

    async def reverse_lookup(self, lat: float, lng: float) -> Address:

        async with self.async_client as client:
            location = GeoLocation(lat=lat, lng=lng)

            data = await client.get(f"{self.url}/reversegeo", params=location.dict())
            return Address(**data.json())
