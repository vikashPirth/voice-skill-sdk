#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#
import pytest
import datetime
from datetime import timedelta
from dateutil.tz import tzutc, tzoffset

from skill_sdk.intents import entities
from skill_sdk.intents.entities import (
    TimeRange,
    TimeSet,
    AttributeV2,
    on_off_to_boolean,
    rank,
    convert,
)
from skill_sdk.utils.util import mock_datetime_now


class TestEntityOnOff:
    def test_values_on(self):
        for value in ("on", "ON", "On", "true", "TRUE", "True", "1"):
            assert on_off_to_boolean(value) is True

    def test_values_off(self):
        for value in ("off", "OFF", "Off", "false", "FALSE", "False", "0"):
            assert on_off_to_boolean(value) is False

    def test_values_bad(self):
        for value in (" on", "ON ", "", None, "\x00", True, False):
            with pytest.raises(ValueError):
                on_off_to_boolean(value)


class TestEntityRank:
    def test_bad_value(self):
        with pytest.raises(ValueError):
            rank("succ")

    def test_value_min(self):
        assert rank("min") == 0

    def test_value_max(self):
        assert rank("max") == -1

    def test_value_prec(self):
        assert rank("prec") - 2

    def test_value(self):
        for value in ("1", "5", "8"):
            assert rank(value) == (int(value) - 1)


class TestEntityTimeRange:
    def test_init(self):
        r = TimeRange("2019-02-08T12:27:20Z/2019-02-08T13:27:20Z")
        assert r.begin == datetime.datetime(
            year=2019, month=2, day=8, hour=12, minute=27, second=20, tzinfo=tzutc()
        )
        assert r.end == datetime.datetime(
            year=2019, month=2, day=8, hour=13, minute=27, second=20, tzinfo=tzutc()
        )
        assert TimeRange("2019-02-08T12:27:20Z/2019-02-08T13:27:20Z") == r
        assert r != 1

    def test_contains(self):
        r = TimeRange("2019-02-08T12:27:20/2019-02-08T13:27:20")
        assert datetime.datetime(year=2019, month=2, day=8, hour=12, minute=28) in r
        assert datetime.datetime(year=2019, month=2, day=8, hour=12) not in r
        assert datetime.time(hour=13) in r
        assert datetime.date(year=2019, month=2, day=8) in r

        with pytest.raises(TypeError):
            (2 in r)

        # can't compare offset-naive and offset-aware datetimes
        with pytest.raises(TypeError):
            r = TimeRange("2019-02-08T12:27:20Z/2019-02-08T13:27:20Z")
            assert (
                datetime.datetime(year=2019, month=2, day=8, hour=12, minute=28)
                not in r
            )

    def test_range(self):
        weeks = list(
            TimeRange("2019-02-08T12:27:20/2019-03-01T13:27:20").range("weeks")
        )
        assert weeks == [
            datetime.datetime(year=2019, month=2, day=8, hour=12, minute=27, second=20),
            datetime.datetime(
                year=2019, month=2, day=15, hour=12, minute=27, second=20
            ),
            datetime.datetime(
                year=2019, month=2, day=22, hour=12, minute=27, second=20
            ),
            datetime.datetime(year=2019, month=3, day=1, hour=12, minute=27, second=20),
        ]

        days = list(TimeRange("2019-02-08T12:27:20/2019-02-09T13:27:20").range("days"))
        assert days == [
            datetime.datetime(year=2019, month=2, day=8, hour=12, minute=27, second=20),
            datetime.datetime(year=2019, month=2, day=9, hour=12, minute=27, second=20),
        ]

        hours = list(
            TimeRange("2019-02-08T12:27:20/2019-02-08T15:48:20").range("hours")
        )
        assert hours == [
            datetime.datetime(year=2019, month=2, day=8, hour=12, minute=27, second=20),
            datetime.datetime(year=2019, month=2, day=8, hour=13, minute=27, second=20),
            datetime.datetime(year=2019, month=2, day=8, hour=14, minute=27, second=20),
            datetime.datetime(year=2019, month=2, day=8, hour=15, minute=27, second=20),
        ]

    def test_range_open(self):
        """Test datetime range with open begin/end"""

        open_start = TimeRange("/2019-12-31T23:59:59")
        assert (
            datetime.datetime(year=2019, month=12, day=31, hour=23, minute=59)
            in open_start
        )
        assert datetime.datetime(year=2020, month=1, day=1, hour=12) not in open_start
        assert datetime.time(hour=13) in open_start
        assert datetime.date(year=2019, month=2, day=8) in open_start

        with mock_datetime_now(
            datetime.datetime(year=2019, month=12, day=29, hour=15), datetime
        ):
            days = list(open_start.range("days"))
            assert days == [
                datetime.datetime(year=2019, month=12, day=29, hour=15),
                datetime.datetime(year=2019, month=12, day=30, hour=15),
                datetime.datetime(year=2019, month=12, day=31, hour=15),
            ]

        open_end = TimeRange("2019-12-31T23:59:59/")
        assert (
            datetime.datetime(
                year=2019, month=12, day=31, hour=23, minute=59, second=59
            )
            in open_end
        )
        assert (
            datetime.datetime(
                year=2019, month=12, day=31, hour=23, minute=59, second=58
            )
            not in open_end
        )
        assert datetime.time(hour=23, minute=59, second=59) in open_end
        assert datetime.date(year=2020, month=1, day=1) in open_end

        weeks = open_end.range("weeks")
        assert datetime.datetime(
            year=2019, month=12, day=31, hour=23, minute=59, second=59
        ) == next(weeks)
        assert datetime.datetime(
            year=2020, month=1, day=7, hour=23, minute=59, second=59
        ) == next(weeks)

        with pytest.raises(OverflowError):
            list(weeks)

    def test_str(self):
        r = TimeRange("2019-02-08T12:27:20/2019-03-01T13:27:20")
        assert (
            str(r)
            == '<TimeRange begin="2019-02-08 12:27:20" end="2019-03-01 13:27:20">'
        )


@mock_datetime_now(
    datetime.datetime(year=2019, month=10, day=31, hour=15, tzinfo=tzutc()), datetime
)
class TestEntityTimeSet:
    def test_init(self):
        assert '<TimeSet timex="T08" tz="tzutc()">' == str(TimeSet("T08"))
        timex = TimeSet("T08", tz="Europe/Berlin")
        assert isinstance(timex.tz, datetime.tzinfo)

        with pytest.raises(ValueError):
            TimeSet("Hello").range()

    def test_range(self):
        # Test rrule string representation
        assert "DTSTART:20191031T150000\nRRULE:FREQ=DAILY;UNTIL=99991231T235959" == str(
            TimeSet("T15").range()
        )
        assert "DTSTART:20191101T080000\nRRULE:FREQ=DAILY;UNTIL=99991231T235959" == str(
            TimeSet("T08").range()
        )

        # Jeden Tag um 8 Uhr
        result = list(TimeSet("T08:00+02:00").range(5, until="2019-11-05T12:00Z"))
        dt_test = datetime.datetime(
            year=2019, month=11, day=1, hour=8, tzinfo=tzoffset(None, 7200)
        )
        assert result == [
            dt_test,
            dt_test + timedelta(days=1),
            dt_test + timedelta(days=2),
            dt_test + timedelta(days=3),
            dt_test + timedelta(days=4),
        ]

        # Jeden Freitag um 10 Uhr
        result = list(TimeSet("XXXX-WXX-5T10:00Z").range(until="2019-11-30"))
        dt_test = datetime.datetime(year=2019, month=11, day=1, hour=10, tzinfo=tzutc())
        assert result == [
            dt_test,
            dt_test + timedelta(days=7),
            dt_test + timedelta(days=14),
            dt_test + timedelta(days=21),
            dt_test + timedelta(days=28),
        ]

        with pytest.raises(ValueError):
            list(TimeSet("-W").range(until="2019-11-30"))

        # Jeden Montag bis Freitag
        result = list(TimeSet("(XXXX-WXX-1,XXXX-WXX-5,P4D)").range(8))
        assert result == [
            datetime.datetime(year=2019, month=11, day=1, tzinfo=tzutc()),
            datetime.datetime(year=2019, month=11, day=4, tzinfo=tzutc()),
            datetime.datetime(year=2019, month=11, day=5, tzinfo=tzutc()),
            datetime.datetime(year=2019, month=11, day=6, tzinfo=tzutc()),
            datetime.datetime(year=2019, month=11, day=7, tzinfo=tzutc()),
            datetime.datetime(year=2019, month=11, day=8, tzinfo=tzutc()),
            datetime.datetime(year=2019, month=11, day=11, tzinfo=tzutc()),
            datetime.datetime(year=2019, month=11, day=12, tzinfo=tzutc()),
        ]

        # Jeden Montag 14 bis 18 Uhr '(XXXX-WXX-1T14,XXXX-WXX-1T18,PT4H)'
        result = list(TimeSet("(XXXX-WXX-1T14,XXXX-WXX-1T18,PT4H)").range(6))
        assert result == [
            datetime.datetime(year=2019, month=11, day=4, hour=14, tzinfo=tzutc()),
            datetime.datetime(year=2019, month=11, day=4, hour=15, tzinfo=tzutc()),
            datetime.datetime(year=2019, month=11, day=4, hour=16, tzinfo=tzutc()),
            datetime.datetime(year=2019, month=11, day=4, hour=17, tzinfo=tzutc()),
            datetime.datetime(year=2019, month=11, day=4, hour=18, tzinfo=tzutc()),
            datetime.datetime(year=2019, month=11, day=11, hour=14, tzinfo=tzutc()),
        ]


class TestEntityAttributeV2:
    def test_init(self):
        attr = AttributeV2(
            {
                "id": 0,
                "value": "super rtl",
                "extras": {"literal": "super rtl"},
                "nestedIn": None,
                "overlapsWith": None,
            }
        )
        assert "super rtl" == attr.value
        assert [] == attr.nested_in
        assert [] == attr.overlaps_with
        assert {"literal": "super rtl"} == attr.extras

    def test_init_with_mapper(self):
        attr = AttributeV2(
            {"id": 0, "value": "123456", "nestedIn": [], "overlapsWith": []}, int
        )
        assert attr.value == 123456

    def test_init_with_self(self):
        attr = AttributeV2(
            {"id": 0, "value": "123456", "nestedIn": [], "overlapsWith": []}, int
        )
        assert attr == AttributeV2(attr)

    def test_init_with_kwargs(self):
        attr = AttributeV2("123456", int, id=0, nested_in=[1], overlaps_with=[2])
        assert (
            "AttributeV2(id=0, value=123456, nested_in=[1], overlaps_with=[2], extras=None)"
            == repr(attr)
        )

    def test_equal(self):
        attr = AttributeV2(
            {
                "id": 1,
                "value": "123456",
                "extras": {"literal": "123456"},
                "nestedIn": [1, 2],
                "overlapsWith": [3],
            },
            int,
        )
        assert attr == AttributeV2(
            {
                "id": 1,
                "value": "123456",
                "extras": {"literal": "123456"},
                "nestedIn": [1, 2],
                "overlapsWith": [3],
            },
            int,
        )
        assert attr != 1

    def test_repr(self):
        attr = AttributeV2(
            {"id": 1, "value": "123456", "nestedIn": [1, 2], "overlapsWith": [3]}, int
        )
        assert (
            "AttributeV2(id=1, value=123456, nested_in=[1, 2], overlaps_with=[3], extras=None)"
            == repr(attr)
        )


class TestConverter:
    def test_converter(self):
        assert convert("2106-12-31T12:30", datetime.date) == datetime.date(2106, 12, 31)
        assert convert("2106-12-31T12:30", datetime.datetime) == datetime.datetime(
            2106, 12, 31, 12, 30, 00
        )
        assert convert("2106-12-31T12:30", datetime.time) == datetime.time(12, 30, 00)
        assert convert("2106-12-31T12:30", str) == "2106-12-31T12:30"
        assert convert("12.30", float) == 12.3
        assert convert("off", bool) is False
        assert convert("1", bool) is True
        assert convert("ja", "str") == "ja"
        assert convert("PT1H5M6S", datetime.timedelta) == datetime.timedelta(
            hours=1, minutes=5, seconds=6
        )

        delta = convert("PT1H5M6S", datetime.timedelta)
        assert convert(delta, datetime.timedelta) == delta

        with pytest.raises(ValueError):
            convert("Something", datetime.time)
        with pytest.raises(ValueError):
            convert("12.30", int)
        with pytest.raises(ValueError):
            convert("Ja", bool)
        with pytest.raises(ValueError):
            convert(1, bool)

    def test_datetime(self):
        assert entities.to_datetime("2106-12-31T12:30") == datetime.datetime(
            2106, 12, 31, 12, 30, 00
        )
        assert entities.to_datetime(datetime.date(2106, 12, 31)) == datetime.datetime(
            2106, 12, 31, 00, 00, 00
        )

        now = datetime.datetime.now()
        assert entities.to_datetime(datetime.time(12, 30)) == datetime.datetime(
            now.year, now.month, now.day, 12, 30, 00
        )
        assert entities.to_datetime(["2106-12-31T12:30"]) == datetime.datetime(
            2106, 12, 31, 12, 30, 00
        )
        assert entities.to_datetime(
            ["2106-12-31T12:30", "2116-12-31T12:30"]
        ) == datetime.datetime(2106, 12, 31, 12, 30, 00)
        assert entities.to_datetime(["--12-31"]) == datetime.datetime(
            datetime.datetime.now().year, 12, 31, 00, 00
        )
        assert entities.to_datetime(["--12-31T12:30"]) == datetime.datetime(
            datetime.datetime.now().year, 12, 31, 12, 30
        )
        assert entities.to_datetime([]), datetime.datetime.min

    def test_date(self):
        assert entities.to_date("2106-12-31T12:30") == datetime.date(2106, 12, 31)
        assert entities.to_date(
            datetime.datetime(2106, 12, 31, 12, 30, 00)
        ) == datetime.date(2106, 12, 31)
        assert entities.to_date(["2106-12-31T12:30"]) == datetime.date(2106, 12, 31)
        assert entities.to_date(
            ["2106-12-31T12:30", "2116-12-31T12:30"]
        ) == datetime.date(2106, 12, 31)
        assert entities.to_date(["--12-31"]) == datetime.date(
            datetime.datetime.now().year, 12, 31
        )
        assert entities.to_date(["--12-31T12:30"]) == datetime.date(
            datetime.datetime.now().year, 12, 31
        )
        assert entities.to_date([]) == datetime.date.min

    def test_time(self):
        assert entities.to_time("2106-12-31T12:30") == datetime.time(12, 30)
        assert entities.to_time(
            datetime.datetime(2106, 12, 31, 12, 30, 00)
        ) == datetime.time(12, 30)
        assert entities.to_time(["2106-12-31T12:30"]) == datetime.time(12, 30)
        assert entities.to_time(
            ["2106-12-31T12:30", "2116-12-31T15:30"]
        ) == datetime.time(12, 30)
        assert entities.to_time(["--12-31"]) == datetime.time(0, 0)
        assert entities.to_time(["--12-31T12:30"]) == datetime.time(12, 30)
        assert entities.to_time([]) == datetime.time.min
