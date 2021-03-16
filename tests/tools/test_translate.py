#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

import pathlib
import tempfile
from unittest.mock import patch
import respx
from httpx import Response


from skill_sdk.tools.translate import download_translations


LOCALE_INFO = {
    "supportedLanguages": [{"code": "de"}, {"code": "en"}, {"code": "whateva"}]
}
TRANSLATIONS = [
    {
        "locale": "de",
        "scope": "unnamed-skill",
        "sentences": ["SCHLÜSSEL1", "SCHLÜSSEL2"],
        "tenant": "GLOBAL",
        "tag": "KEY",
    },
    {
        "locale": "en",
        "scope": "unnamed-skill",
        "sentences": ["KEY1", "KEY2"],
        "tenant": "GLOBAL",
        "tag": "KEY",
    },
]


@respx.mock
def test_download_translations():
    respx.get("http://service-text-service:1555/v1/text/info/locale").mock(
        return_value=Response(200, json=LOCALE_INFO)
    )
    respx.get("http://service-text-service:1555/v1/text/scope/unnamed-skill").mock(
        return_value=Response(200, json=TRANSLATIONS)
    )

    with tempfile.TemporaryDirectory() as tmp:
        with patch("skill_sdk.i18n.LOCALE_DIR", tmp):
            download_translations(
                "http://service-text-service:1555/v1/text", "unnamed-skill"
            )
            assert (
                pathlib.Path(tmp) / "en.yaml"
            ).read_text() == "KEY:\n- KEY1\n- KEY2\n"
            assert (
                pathlib.Path(tmp) / "de.yaml"
            ).read_text() == "KEY:\n- SCHLÜSSEL1\n- SCHLÜSSEL2\n"
            assert (pathlib.Path(tmp) / "whateva.yaml").exists() is False
