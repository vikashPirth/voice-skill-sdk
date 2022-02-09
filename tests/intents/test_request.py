#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

import os
import time
import asyncio
import logging
import datetime
import threading
from unittest.mock import patch
from dateutil import tz
import pytest

from skill_sdk.intents import RequestContextVar, request
from skill_sdk.utils.util import (
    create_context,
    create_request,
    mock_datetime_now,
)
from skill_sdk.i18n import Translations

logger = logging.getLogger(__name__)


class TestContext:
    @pytest.fixture
    def context(self):
        return create_context("Testing__Intent")

    def test_tz_functions(self, context):
        now = datetime.datetime(
            year=2100, month=12, day=19, hour=23, minute=42, tzinfo=tz.tzutc()
        )

        assert "CET" == context.gettz().tzname(now)
        ctx = create_context("Testing__Intent", timezone="Mars")
        with patch.object(logging.Logger, "error") as log:
            assert "UTC" == ctx.gettz().tzname(now)
            assert log.call_count == 1

        with mock_datetime_now(now, datetime):
            # Make sure timezone is set to "Europe/Berlin"
            assert context.attributes.get("timezone") == ["Europe/Berlin"]
            assert context.gettz().tzname(now) == "CET"
            ctx = create_context("Testing__Intent", timezone="Europe/Athens")
            assert isinstance(ctx.gettz(), datetime.tzinfo)

            with patch.dict(os.environ, {"TZ": "UTC"}):
                time.tzset()
                local_now = ctx.now()
                assert local_now == now
                assert local_now.day == 20
                assert local_now.hour == 1

                local_today = ctx.today()
                assert local_today.day == 20
                assert local_today.hour == 0
                assert local_today.minute == 0

    def test_missing_attribute(self, context):
        assert "Value" == context._get_attr_value("Non-existing", "Value")


def run_thread(func):
    t = threading.Thread(target=func)
    t.start()
    t.join()


class TestContextLocal:
    now = datetime.datetime(
        year=2100, month=12, day=19, hour=23, minute=42, tzinfo=datetime.timezone.utc
    )

    def setup_method(self):
        req = create_request("TELEKOM_Demo_Intent", timezone=["Europe/Berlin"])

        @mock_datetime_now(self.now, datetime)
        def run():
            now = self.now.astimezone(datetime.timezone(datetime.timedelta(hours=1)))
            with RequestContextVar(request=req):
                assert (
                    request.context.today().timestamp()
                    == now.replace(hour=0, minute=0, tzinfo=None).timestamp()
                )
                assert request.context.now().timestamp() == self.now.timestamp()

        run_thread(run)

    @mock_datetime_now(now, datetime)
    def test_context_local_now(self):
        req = create_request("TELEKOM_Demo_Intent", timezone=["Europe/Athens"])
        next_day = datetime.datetime(year=2100, month=12, day=20, hour=0, minute=0)
        with RequestContextVar(request=req):
            assert request.context.today().timestamp() == next_day.timestamp()
            assert request.context.now().timestamp(), self.now.timestamp()

    @patch.object(logging.Logger, "error")
    def test_context_local_context(self, err_mock):
        assert request.context is None
        err_mock.assert_called_with(
            "Accessing request local object outside of the request-response cycle."
        )
        req = create_request(
            "TELEKOM_Demo_Intent", session={"key-1": "value-1", "key-2": "value-2"}
        )
        with RequestContextVar(request=req):
            assert request.context.intent == "TELEKOM_Demo_Intent"
            assert {
                "id": "123",
                "attributes": {"key-1": "value-1", "key-2": "value-2"},
                "new": True,
            } == request.session.dict()

        with RequestContextVar(request=req.with_translation(Translations())):
            assert "HELLO" == request.context._("HELLO")
            assert "HELLO" == request.context._n("HELLO", "HOLA", 1)
            assert ["HELLO"] == request.context._a("HELLO")


@pytest.mark.asyncio
async def test_context_local_session():
    async def one(_):
        with RequestContextVar(request=_):
            del request.session["key-1"]
            del request.session["key-2"]
            assert request.session.dict() == {
                "id": "123",
                "attributes": {},
                "new": True,
            }

    async def init(_):
        with RequestContextVar(request=_):
            with pytest.raises(TypeError):
                request.context.locale = "de"  # noqa: attempt to modify "read-only" context (to raise TypeError)

            assert request.session.dict() == {
                "id": "123",
                "attributes": {"key-1": "value-1", "key-2": "value-2"},
                "new": True,
            }

    async def two(_):
        with RequestContextVar(request=_):
            request.session["key-1"] = "value-12"
            request.session["key-2"] = "value-22"
            assert request.session.dict() == {
                "id": "123",
                "attributes": {"key-1": "value-12", "key-2": "value-22"},
                "new": True,
            }

    req = create_request(
        "TELEKOM_Demo_Intent", session={"key-1": "value-1", "key-2": "value-2"}
    )

    await asyncio.gather(
        init(req),
        one(req),
        two(req),
        init(req),
        one(req),
        two(req),
        init(req),
        one(req),
        two(req),
        init(req),
        one(req),
        two(req),
    )
