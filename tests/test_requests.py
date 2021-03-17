#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

import unittest
from unittest.mock import patch, ANY
import pytest

import httpx
import respx

import skill_sdk.requests
from skill_sdk.requests import (
    Client,
    AsyncClient,
    CircuitBreaker,
    CircuitBreakerState,
    HTTPError,
    DEFAULT_CIRCUIT_BREAKER,
    DEFAULT_REQUESTS_TIMEOUT,
)


LOCALHOST = "http://localhost/"


class TestClient(unittest.TestCase):
    def test_init(self):
        zcbs = Client()
        self.assertEqual(zcbs.circuit_breaker, DEFAULT_CIRCUIT_BREAKER)
        self.assertTrue(isinstance(zcbs, Client))

    def test_init_with_circuit_breaker(self):
        cb = CircuitBreaker()
        zcbs = Client(circuit_breaker=cb)
        self.assertEqual(zcbs.circuit_breaker, cb)
        self.assertTrue(isinstance(zcbs, Client))

    @respx.mock
    def test_request_default(self):
        route = respx.get(LOCALHOST).mock()
        with Client() as c:
            c.get(LOCALHOST)
            assert route.called

    @patch.object(httpx.Client, "request")
    def test_request_timeout_if_set(self, client_mock):
        with Client(timeout=6.6) as s:
            s.get(LOCALHOST)
            client_mock.assert_called_once_with(
                "GET",
                LOCALHOST,
                allow_redirects=True,
                timeout=httpx.Timeout(6.6),
                params=None,
                headers=None,
                cookies=None,
                auth=ANY,
            )

    @patch.object(httpx.Client, "request")
    @patch.object(skill_sdk.requests, "DEFAULT_REQUESTS_TIMEOUT", 10)
    def test_request_timeout_from_config(self, client_mock):
        with Client() as s:
            s.get(LOCALHOST)
            client_mock.assert_called_once_with(
                "GET",
                LOCALHOST,
                allow_redirects=True,
                timeout=httpx.Timeout(10),
                params=None,
                headers=None,
                cookies=None,
                auth=ANY,
            )

    @respx.mock
    def test_check_raise(self):
        route = respx.get(LOCALHOST).mock(return_value=httpx.Response(500))
        with self.assertRaises(Exception):
            Client().get(LOCALHOST)
        assert route.called

    @patch.object(skill_sdk.requests, "warn")
    def test_deprecation_warning(self, warn):
        from skill_sdk.requests import CircuitBreakerSession

        with CircuitBreakerSession() as s:
            self.assertEqual(1, warn.call_count)


@respx.mock
@pytest.mark.asyncio
async def test_async_request_ok():
    route = respx.get(LOCALHOST).mock()
    async with AsyncClient() as c:
        r = await c.get(LOCALHOST)
        assert route.called
        assert r.status_code == 200


@respx.mock
@pytest.mark.asyncio
async def test_async_request_fail():
    route = respx.get(LOCALHOST).mock(return_value=httpx.Response(500))
    async with AsyncClient() as c:
        with pytest.raises(Exception):
            await c.get(LOCALHOST)
        assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_request_fail_with_exclusion():
    route = respx.get(LOCALHOST).mock(return_value=httpx.Response(404))
    with Client(exclude=[httpx.codes.NOT_FOUND]) as c:
        c.get(LOCALHOST)
        assert route.called
    async with AsyncClient(exclude=[httpx.codes.NOT_FOUND]) as c:
        await c.get(LOCALHOST)
        assert route.called