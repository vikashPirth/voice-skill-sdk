from unittest.mock import patch, mock_open
import unittest.mock
import tempfile

from skill_sdk import config

CONFIG_INI = """
[key]
subkey = value

[key2]
subkey2 = ${ENV_VAR:default/{0}/items}

[key3]
subkey3 = ${ENV_VAR_WITHOUT_DEFAULT}
"""


class TestLoadConfig(unittest.TestCase):
    def test_get_config_file(self):
        self.assertEqual(config.get_skill_config_file(), config.SKILL_CONFIG_FILE)
        with patch("os.environ", new={"CONFIG_FILE": "config.file"}):
            self.assertEqual("config.file", config.get_skill_config_file())

    def test_init_config(self):
        with patch("builtins.open", mock_open(read_data="[skill]\nid=skill")):
            self.assertEqual("skill", config.init_config("some_file")["skill"]["id"])
        with patch("builtins.open", side_effect=FileNotFoundError):
            with self.assertRaises(RuntimeError):
                config.get_skill_config_file("some_file")

    def test_read_config(self):
        with patch("builtins.open", mock_open(read_data=CONFIG_INI)):
            self.assertEqual(
                ["key", "key2", "key3"], config.read_config("path").sections()
            )
        with patch("builtins.open", mock_open(read_data=CONFIG_INI)), patch(
            "os.environ", new={"ENV_VAR": "environment_variable"}
        ):
            self.assertEqual(
                "environment_variable", config.read_config("path")["key2"]["subkey2"]
            )
        with patch("builtins.open", side_effect=FileNotFoundError):
            self.assertEqual([], config.read_config("path").sections())

    def test_load_additional(self):
        with patch("builtins.open", mock_open(read_data=CONFIG_INI)):
            with tempfile.TemporaryDirectory() as tmp_dir, tempfile.NamedTemporaryFile(
                dir=tmp_dir, suffix=".conf"
            ) as tmp_file, tempfile.NamedTemporaryFile(
                dir=tmp_dir, suffix=".noconf"
            ), patch(
                "os.environ",
                new={"CONFIG_ADDITIONAL_LOCATION": f"{tmp_dir}, path_dont_exist"},
            ):
                self.assertEqual([tmp_file.name], config.load_additional())

        with patch("os.environ", new={"CONFIG_ADDITIONAL_LOCATION": ""}):
            self.assertFalse(config.load_additional())


def test_extra_attributes_allowed(monkeypatch):
    from skill_sdk.config import settings, Settings

    # Should not raise ValueError: "Settings" object has no field "NEW_KID_ON_THE_BLOCK"
    settings.NEW_KID_ON_THE_BLOCK = "1"

    # Configuration can be also loaded from a dictionary-like object
    monkeypatch.setattr(
        Settings.Config, "conf_file", {"new-section": {"my-key": "value"}}
    )
    settings = Settings()
    assert settings.NEW_SECTION_MY_KEY == "value"  # noqa
