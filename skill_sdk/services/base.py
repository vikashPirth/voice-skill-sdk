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
# Base service
#

import logging
from typing import Dict, Optional, Text

from skill_sdk.intents import r
from skill_sdk.requests import AsyncClient, Client

logger = logging.getLogger(__name__)

AUTH_TOKEN = "cvi"

# Default timeout when accessing the service
DEFAULT_SERVICE_TIMEOUT = 10


class BaseService:
    """
    The base for cloud services

    """

    # Service version
    VERSION: int = 0

    # Service name
    NAME: Text = "base"

    # Service URL
    url: Text

    # Default request headers
    _headers: Dict[Text, Text] = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Timeout value
    timeout: float = DEFAULT_SERVICE_TIMEOUT

    #
    # Specifies if authorization header should be added to the request
    #
    add_auth_header: bool = True

    def __init__(
        self,
        url: Text,
        timeout: float = DEFAULT_SERVICE_TIMEOUT,
        headers: Dict[Text, Text] = None,
        add_auth_header=True,
    ) -> None:
        self.url = url
        self.timeout = timeout
        self.add_auth_header = add_auth_header
        if headers:
            self._headers = {**self._headers, **headers}

    @staticmethod
    def auth_header():
        """Add "Authorization" header for bearer auth

        :return:
        """

        # Get CVI token from current request
        try:
            token = r.context.tokens[AUTH_TOKEN]
            logger.debug("Adding auth token to authorization header.")
            return {"Authorization": f"Bearer {token}"}
        except (AttributeError, KeyError):
            logger.error("No auth token found in the current request.")
            return {}

    @property
    def headers(self) -> Dict:
        headers = (
            {**self._headers, **self.auth_header()}
            if self.add_auth_header
            else self._headers
        )
        logger.debug("Client headers: %s", repr(headers))
        return headers

    @property
    def client(self) -> Client:
        """Creates and new client with circuit breaker"""

        return Client(headers=self.headers, timeout=self.timeout)

    @property
    def async_client(self) -> AsyncClient:
        """Creates new async client with circuit breaker"""

        return AsyncClient(headers=self.headers, timeout=self.timeout)
