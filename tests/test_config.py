#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

from unittest.mock import patch, mock_open
import tempfile
import pytest

from skill_sdk import config

CONFIG_INI = """
[key]
subkey = value

[key2]
subkey2 = ${ENV_VAR:default/{0}/items}

[key3]
subkey3 = ${ENV_VAR_WITHOUT_DEFAULT}
"""


def test_get_config_file(monkeypatch):
    assert config.get_skill_config_file() == config.SKILL_CONFIG_FILE
    monkeypatch.setenv("CONFIG_FILE", "config.file")
    assert config.get_skill_config_file() == "config.file"


def test_init_config():
    with patch("builtins.open", mock_open(read_data="[skill]\nid=skill")):
        assert config.init_config("some_file")["skill"]["id"] == "skill"
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(RuntimeError):
            config.get_skill_config_file("some_file")


def test_read_config(monkeypatch):
    with patch("builtins.open", mock_open(read_data=CONFIG_INI)):
        assert config.read_config("path").sections() == ["key", "key2", "key3"]

    with patch("builtins.open", mock_open(read_data=CONFIG_INI)):
        monkeypatch.setenv("ENV_VAR", "environment_variable")
        assert config.read_config("path")["key2"]["subkey2"] ==  "environment_variable"

    with patch("builtins.open", side_effect=FileNotFoundError):
        assert config.read_config("path").sections() == []


def test_load_additional(monkeypatch):
    with patch("builtins.open", mock_open(read_data=CONFIG_INI)):
        with tempfile.TemporaryDirectory() as tmp_dir, tempfile.NamedTemporaryFile(
                dir=tmp_dir, suffix=".conf"
        ) as tmp_file, tempfile.NamedTemporaryFile(
            dir=tmp_dir, suffix=".noconf"
        ):
            monkeypatch.setenv("CONFIG_ADDITIONAL_LOCATION", f"{tmp_dir}, path_dont_exist")
            assert config.load_additional() == [tmp_file.name]

    monkeypatch.setenv("CONFIG_ADDITIONAL_LOCATION", "")
    assert bool(config.load_additional()) is False


def test_extra_attributes_allowed(monkeypatch):
    from skill_sdk.config import settings, Settings

    # Should not raise ValueError: "Settings" object has no field "NEW_KID_ON_THE_BLOCK"
    settings.NEW_KID_ON_THE_BLOCK = "1"

    # Configuration can be also loaded from a dictionary-like object
    monkeypatch.setattr(
        Settings.Config, "conf_file", {"new-section": {"my-key": "value"}}
    )
    s = Settings()
    assert s.NEW_SECTION_MY_KEY == "value"  # noqa


def test_dot_env(monkeypatch, tmp_path):
    from skill_sdk.config import Settings

    monkeypatch.chdir(tmp_path)
    (tmp_path / "skill.conf").write_text("""
    [new]
    key = Value
    """)
    (tmp_path / ".env").write_text("""
        SKILL_NAME = My Awesome Skill
        NEW_KEY = New Value
    """)
    s = Settings()
    assert s.SKILL_NAME == "My Awesome Skill"
