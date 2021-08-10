#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

from contextlib import closing

import pytest
from skill_sdk import skill


@pytest.fixture
def app():
    with closing(skill.init_app(develop=True)) as app:
        yield app
