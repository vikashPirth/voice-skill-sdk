#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

from unittest.mock import patch

import pytest
from pytest import CaptureFixture
from skill_sdk.__main__ import main
from skill_sdk.cli import init, develop, run, translate, version


@pytest.mark.parametrize(
    "argv, module",
    [
        (["vs", "init"], init),
        (["vs", "run", "impl"], run),
        (["vs", "develop", "impl"], develop),
        (["vs", "translate", "impl"], translate),
        (["vs", "version"], version),
    ],
)
def test_main(argv, module):
    with patch("sys.argv", new=argv):
        with patch.object(module, "execute") as mock:
            main()
            mock.assert_called_once()


def test_help(capsys: CaptureFixture):
    with patch("sys.argv", new=["vs", "don't know"]):
        with pytest.raises(SystemExit):
            main()
    with patch("sys.argv", new=["vs", "--help"]):
        with pytest.raises(SystemExit):
            main()
    out = capsys.readouterr()
    assert (
        "usage: vs [-h] [-v] [-vv] [-q] {init,run,develop,translate,version}" in out.out
    )
