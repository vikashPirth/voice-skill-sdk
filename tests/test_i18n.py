#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#
import datetime
import unittest
import pathlib
import subprocess
from unittest.mock import patch, mock_open, MagicMock
import yaml
import pytest

from skill_sdk import i18n
from skill_sdk.utils import util
from skill_sdk.i18n import (
    PROGRAM,
    _load_yaml,
    _load_gettext,
    Message,
    Translations,
    MultiStringTranslation,
    _,
    _n,
    _a,
)
from skill_sdk.tools.translate import (
    translate_locale,
    init_locales,
    extract_translations,
    update_translation,
)

# Content of an empty .mo file
EMPTY_MO_DATA = (
    b"\xde\x12\x04\x95\x00\x00\x00\x00\x01\x00\x00\x00\x1c\x00\x00\x00$\x00\x00\x00\x03\x00\x00\x00,"
    b"\x00\x00\x00\x00\x00\x00\x008\x00\x00\x00(\x00\x00\x009\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00Content-Type: text/plain; charset=UTF-8\n\x00"
)

TEST_YAML_DATA = """
KEY1:
    - VALUE11
    - VALUE12
KEY2:
    - VALUE21
    - VALUE22
"""

TEST_ALL_DATA = """
zh:
    KEY1:
        - VALUE11
        - VALUE12
    KEY2:
        - VALUE21
        - VALUE22
bb:
    KEY1: VALUEBB        
"""


class TestI18n:
    @patch("subprocess.check_output")
    @patch("skill_sdk.i18n._load_all", return_value={})
    @patch("skill_sdk.i18n._load_yaml", return_value={})
    @patch("skill_sdk.i18n.Path.open", mock_open(read_data=EMPTY_MO_DATA), create=True)
    def test_load_gettext_translations(self, *args):
        mock = MagicMock()
        mock.glob.return_value = [pathlib.Path("zh.mo")]
        with patch("skill_sdk.i18n.get_locale_dir", return_value=mock):
            assert {
                "": "Content-Type: text/plain; charset=UTF-8\n"
            } == i18n.load_translations()["zh"]._catalog
            mock.glob.return_value = [pathlib.Path("bad_lang_code.mo")]
            assert i18n.load_translations() == {}

    def test_load_all_translations(self):
        with patch("pathlib.io.open", mock_open(read_data=TEST_ALL_DATA), create=True):
            tr = i18n.load_translations()
        assert tr["bb"].gettext("KEY1") == "VALUEBB"
        assert tr["zh"].getalltexts("KEY2") == ["VALUE21", "VALUE22"]  # noqa

        data = yaml.safe_load(TEST_ALL_DATA)
        with patch(
            "pathlib.io.open",
            mock_open(read_data=yaml.safe_dump({**data, **{"invalid": {}}})),
            create=True,
        ), pytest.raises(RuntimeError):
            i18n.load_translations()

    @patch("builtins.open", mock_open(read_data=EMPTY_MO_DATA), create=True)
    def test_make_lazy_translation(self):
        from skill_sdk.intents import RequestContextVar

        tr = Translations("de.mo")
        request = util.create_request("Test__Intent")
        tr._catalog["KEY"] = "VALUE"
        tr._catalog[("KEY", 1)] = "VALUES"
        tr._catalog["KEY_PLURAL"] = "VALUES"
        assert _("KEY") == "KEY"
        assert _n("KEY", "KEY_PLURAL", 1) == "KEY"
        assert _n("KEY", "KEY_PLURAL", 2) == "KEY_PLURAL"
        assert _a("KEY") == ["KEY"]
        with RequestContextVar(request=request.with_translation(tr)):
            assert _("KEY") == "VALUE"
            assert _n("KEY", "KEY_PLURAL", 2) == "VALUES"
            assert _a("KEY") == ["KEY"]

    @patch("subprocess.check_output", return_value=0)
    def test_extract_translations(self, process):
        extract_translations(["a.py", "b.my"])
        process.assert_called_once_with(
            [
                PROGRAM,
                "extract",
                "--input-dirs=a.py,b.my",
                "--output=locale/messages.pot",
            ],
            text=True,
            stderr=subprocess.STDOUT,
        )

        with patch.object(pathlib.Path, "exists", return_value=False), patch.object(
            pathlib.Path, "mkdir"
        ) as mkdir:
            extract_translations(["a.py", "b.my"])
            mkdir.assert_called_once_with(parents=True)

        process.reset_mock()
        extract_translations(["impl"])
        process.assert_called_once_with(
            [PROGRAM, "extract", "--input-dirs=impl", "--output=locale/messages.pot"],
            text=True,
            stderr=subprocess.STDOUT,
        )

        extract_translations(["a.py", "b.my"])
        process.side_effect = FileNotFoundError()
        assert extract_translations(["a.py"]) is None
        process.side_effect = subprocess.CalledProcessError(1, cmd="")
        assert extract_translations(["a.py"]) is None

    @patch("subprocess.check_call", return_value=0)
    def test_init_locales(self, process):
        init_locales(pathlib.Path("template"), ["en", "de"])
        process.assert_any_call(
            [
                PROGRAM,
                "init",
                "--locale=en",
                "--input-file=template",
                "--output-file=locale/en.po",
            ]
        )
        process.assert_any_call(
            [
                PROGRAM,
                "init",
                "--locale=de",
                "--input-file=template",
                "--output-file=locale/de.po",
            ]
        )
        process.side_effect = subprocess.CalledProcessError(1, cmd="")
        assert (init_locales(pathlib.Path("template"), ["en", "de"])) is False
        process.side_effect = FileNotFoundError()
        with patch.object(pathlib.Path, "exists", return_value=True), patch.object(
            pathlib.Path, "unlink"
        ) as unlink_mock:
            assert (
                init_locales(pathlib.Path("template"), ["en", "de"], force=True)
                is False
            )
            unlink_mock.assert_called_once()

    def test_update_translations(self, caplog):
        with patch.object(
            pathlib.Path,
            "open",
            mock_open(
                read_data='msgid "TEST" \n  msgstr "" \n\n msgid "TEST1" \n  msgstr "" \n'
            ),
        ):
            result = translate_locale("en", {"TEST": "Test Translation"})
            assert result == [
                'msgid "TEST" \n',
                'msgstr "Test Translation"',
                "\n",
                ' msgid "TEST1" \n',
                '  msgstr "" \n',
            ]

            # Intentionally using list to raise AttributeError:
            assert (translate_locale("en", [])) is None
        with patch.object(
            pathlib.Path,
            "open",
            mock_open(
                read_data='msgid "TEST" \n  msgstr "" \n\n msgid "TEST1" \n  msgstr "" \n'
            ),
        ) as open_mock:
            update_translation("en", {"TEST": "Test Translation"})
            open_mock().writelines.assert_called_once_with(
                [
                    'msgid "TEST" \n',
                    'msgstr "Test Translation"',
                    "\n",
                    ' msgid "TEST1" \n',
                    '  msgstr "" \n',
                ]
            )

    def test_strings_escape(self):
        with patch.object(
            pathlib.Path, "open", mock_open(read_data='msgid "TEST" \n  msgstr "" \n\n')
        ):
            result = translate_locale(
                "en",
                {
                    "TEST": [
                        "Test Translation with 'quotes' and \"doubles\"",
                        "Second translation without both",
                    ]
                },
            )
            assert result == [
                'msgid "TEST" \n',
                'msgstr "Test Translation with \'quotes\' and \\"doubles\\""',
                "\n",
            ]

            result = translate_locale(
                "en",
                {"TEST": ["\nMulti-line string\nWith loads of things here and there "]},
            )
            assert result == [
                'msgid "TEST" \n',
                'msgstr "Multi-line string"\n"With loads of things here and there"',
                "\n",
            ]

    @patch("subprocess.run", side_effect=FileNotFoundError)
    def test_compile_locales(self, *args):
        assert i18n.compile_locales() is None


class TestMessage:
    def test_message_new(self):
        assert " " == Message(" ")
        message = Message("{a}=={b}", a="1", b="1")
        assert message == "1==1"
        assert message.key == "{a}=={b}"
        assert message.kwargs == {"a": "1", "b": "1"}
        message = Message("{0}!={1}", "key", "0", "1")
        assert message == "0!=1"
        assert message.key == "key"
        assert message.args == ("0", "1")
        assert message.kwargs == {}

        message = "Chuck Norris can instantiate interfaces"
        assert Message(message) == message
        assert Message(message).key == message

    def test_message_simple_format(self):
        message = Message("{a}=={b}", "key").format(a="1", b="1")
        assert message == "1==1"
        assert message.key == "key"
        assert message.kwargs == {"a": "1", "b": "1"}
        message = Message("{0}!={1}", "key").format("0", "1")
        assert message == "0!=1"
        assert message.args == ("0", "1")
        assert message.kwargs == {}

    def test_message_extended_format(self):
        message1 = Message("{a}=={b}", a="1", b="1")
        message2 = Message("{c}=={d}", c="2", d="2")
        message3 = Message("{e}=={f}", e="3", f="3")

        with pytest.raises(TypeError):
            Message("").join(None)
        assert "1==1" == Message(" ").join((message1,))
        assert "1==1 2==2" == Message(" ").join((message1, message2))
        assert "1==1 2==2 3==3" == Message(" ").join((message1, message2, message3))

    def test_strip(self):
        assert "Message" == Message(" !Message?!,. ").strip(" !?,.")

    def test_add(self):
        m = Message("1") + " " + Message("2")
        assert "1 2" == m
        assert '1 " " 2' == m.key
        m = Message("1") + " " + "2"
        assert "1 2" == m
        assert '1 " " "2"' == m.key
        m = "1" + " " + Message("2")
        assert "1 2" == m
        assert isinstance(m, str)

        m = Message("A", "B") + Message("C", "D")
        assert "AC" == m
        assert "B D" == m.key
        m = Message("Hi!") + Message("By.")
        assert "Hi!By." == m
        assert "Hi! By." == m.key

        m = Message("MYTAG1") + "some text" + Message("MYTAG2")
        assert "MYTAG1some textMYTAG2" == m
        assert 'MYTAG1 "some text" MYTAG2' == m.key

        m = Message("MYTAG1") + " some text " + Message("MYTAG2")
        assert "MYTAG1 some text MYTAG2" == m
        assert 'MYTAG1 " some text " MYTAG2' == m.key

        with pytest.raises(TypeError):
            Message("1") + 1

        m = Message("1") + ""
        assert "1" == m
        assert "1" == m.key

        m = Message("") + "1"
        assert "1" == m
        assert '"1"' == m.key


class TestTranslations(unittest.TestCase):
    @patch("subprocess.check_output")
    @patch("pathlib.io.open", mock_open(read_data=EMPTY_MO_DATA), create=True)
    def setUp(self, *args) -> None:
        mock = MagicMock()
        mock.glob.return_value = [pathlib.Path("zh.mo")]
        with patch("skill_sdk.i18n.get_locale_dir", return_value=mock):
            self.tr = _load_gettext()["zh"]

    def test_message_gettext(self):
        message = self.tr.gettext("KEY", a="1", b="1")
        self.assertEqual(message, "KEY")
        self.assertEqual(message.key, "KEY")
        self.assertEqual(message.kwargs, {"a": "1", "b": "1"})

    def test_message_ngettext(self):
        message = self.tr.ngettext("KEY1", "KEY2", 1, a="1", b="1")
        self.assertEqual(message, "KEY1")
        self.assertEqual(message.key, "KEY1")
        self.assertEqual(message.kwargs, {"a": "1", "b": "1"})


class TestMultiStringTranslation(unittest.TestCase):
    @patch("pathlib.io.open", mock_open(read_data=TEST_YAML_DATA), create=True)
    def setUp(self, *args) -> None:
        mock = MagicMock()
        mock.glob.return_value = [pathlib.Path("zh.yaml")]
        with patch("skill_sdk.i18n.get_locale_dir", return_value=mock):
            self.tr = _load_yaml().get("zh")

    def test_load_invalid_yaml(self):
        with patch(
            "pathlib.io.open", mock_open(read_data="blah-blah\nblah:"), create=True
        ):
            mock = MagicMock()
            mock.glob.return_value = [pathlib.Path("zh.yaml")]
            with patch("skill_sdk.i18n.get_locale_dir", return_value=mock):
                with self.assertRaises(RuntimeError):
                    _load_yaml()

    def test_from_dict(self):
        data = yaml.safe_load(TEST_YAML_DATA)
        tr = MultiStringTranslation.from_dict("de", {"de": data})
        self.assertEqual(tr.getalltexts("KEY1"), ["VALUE11", "VALUE12"])

        with self.assertRaises(RuntimeError):
            MultiStringTranslation.from_dict("zh", {"de": {}})

    def test_message_gettext(self):
        with patch("skill_sdk.i18n.random.choice", return_value="WHATEVA"):
            message = self.tr.gettext("KEY1", a="1", b="1")
        self.assertEqual(message.key, "KEY1")
        self.assertEqual(message.value, "WHATEVA")
        self.assertEqual(message.kwargs, {"a": "1", "b": "1"})

        self.assertEqual("KEY3", self.tr.gettext("KEY3"))

    def test_message_ngettext(self):
        with patch("skill_sdk.i18n.random.choice", return_value="WHATEVA"):
            message = self.tr.ngettext("KEY1", "KEY2", 1, a="1", b="1")
        self.assertEqual(message.key, "KEY1")
        self.assertEqual(message.value, "WHATEVA")
        self.assertEqual(message.kwargs, {"a": "1", "b": "1"})

    def test_message_getalltexts(self):
        message = self.tr.getalltexts("KEY1")
        self.assertEqual(message[0].key, "KEY1")
        self.assertEqual(message[1].key, "KEY1")
        self.assertEqual(message[0].value, "VALUE11")
        self.assertEqual(message[1].value, "VALUE12")

        self.assertEqual(["KEY3"], self.tr.getalltexts("KEY3"))


class TestFormatFunctions(unittest.TestCase):
    def setUp(self) -> None:
        self.tr = Translations()
        self.tr.lang = "en"

    def test_format_list(self):
        self.assertEqual("", self.tr.format_list([]))
        self.assertEqual("dog and fox", self.tr.format_list(["dog", "fox"]))
        self.assertEqual(
            "cat, dog, and fox", self.tr.format_list(["cat", "dog", "fox"])
        )

    def test_nl_build(self):
        with self.assertRaises(TypeError):
            self.assertEqual(self.tr.nl_build("Header"), "")

        self.assertEqual(
            "Chuck Norris can: instantiate interfaces.",
            self.tr.nl_build("Chuck Norris can", ["instantiate interfaces"]),
        )
        self.assertEqual(
            "Chuck Norris can: instantiate interfaces and jump over the lazy fox.",
            self.tr.nl_build(
                "Chuck Norris can", ["instantiate interfaces", "jump over the lazy fox"]
            ),
        )
        self.assertEqual(
            "Chuck Norris can: instantiate interfaces, jump over the lazy fox, and play with fox.",
            self.tr.nl_build(
                "Chuck Norris can", ["instantiate interfaces", "jump over the lazy fox", "play with fox"]
            ),
        )

    @util.mock_datetime_now(
        datetime.datetime(year=2100, month=12, day=31, hour=15), datetime
    )
    def test_format_datetime(self):
        self.assertEqual(
            "Dec 31, 2100, 3:00:00 PM", self.tr.format_datetime(datetime.datetime.now())
        )
        self.assertEqual("3:00:00 PM", self.tr.format_time(datetime.datetime.now()))
        self.assertEqual("Dec 31, 2100", self.tr.format_date(datetime.datetime.now()))
