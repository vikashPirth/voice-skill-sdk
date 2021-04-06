#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

"""Geolocation service"""

import logging
from typing import Optional, Text

from skill_sdk.util import CamelModel
from skill_sdk.services.base import BaseService

logger = logging.getLogger(__name__)


#
#   The models below reflect location service's response structure
#


class GeoLocation(CamelModel):
    """Geo-location: latitude/longitude"""

    lat: float
    lng: float


class AddressComponents(CamelModel):
    """Address components: city and postal code"""

    city: Text
    postal_code: Text


class Address(CamelModel):
    """Address: country with address components"""

    country: Text
    address_components: AddressComponents


class Location(CamelModel):
    """Location consists of an address and time-zone"""

    address: Address
    timezone: Text = "Europe/Berlin"


class FullLocation(GeoLocation, Location):
    """Full location consists of an address component and geographical coordinates"""

    ...


class GeoLookupQuery(CamelModel):
    """Request to location service"""

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
        """
        Forward lookup: resolve geo-coordinates from textual address components

        :param country:
        :param city:
        :param postalcode:
        :param lang:
        :return:
        """
        async with self.async_client as client:
            params = GeoLookupQuery(
                country=country, city=city, postalcode=postalcode, lang=lang
            )

            data = await client.get(f"{self.url}/geo", params=params.dict())
            return FullLocation(**data.json())

    async def reverse_lookup(self, lat: float, lng: float) -> Address:
        """
        Reverse lookup: resolve address components from geo-coordinates

        :param lat:
        :param lng:
        :return:
        """

        async with self.async_client as client:
            location = GeoLocation(lat=lat, lng=lng)

            data = await client.get(f"{self.url}/reversegeo", params=location.dict())
            return Address(**data.json())
