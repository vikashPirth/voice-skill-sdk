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

from skill_sdk.responses import SkillInfoResponse
from skill_sdk.__version__ import __spi_version__


def test_info():
    info = SkillInfoResponse(
        skill_id="test-skill", skill_version="0.1", supported_locales=("de", "en")
    )
    assert info.dict(by_alias=True) == {
        "skillId": "test-skill",
        "skillVersion": "0.1",
        "supportedLocales": ("de", "en"),
        "skillSpiVersion": __spi_version__,
    }

    with pytest.raises(TypeError):
        info.skill_version = 0.2
