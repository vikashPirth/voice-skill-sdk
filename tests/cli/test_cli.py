#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

import os
import sys
import pathlib
import pkg_resources
from argparse import Namespace

import pytest
from pytest import CaptureFixture

from skill_sdk.config import settings
from skill_sdk.cli import import_module_app, develop, init, run, version
from skill_sdk.util import run_until_complete

APP = "app:app"


@pytest.fixture
def debug_logging(monkeypatch):
    from skill_sdk import log

    monkeypatch.setattr(settings, "LOG_LEVEL", "DEBUG")
    monkeypatch.setattr(settings, "LOG_FORMAT", "human")
    log.setup_logging()
    return True


def test_import_module_app():

    sdk, _ = import_module_app("skill_sdk")
    import skill_sdk

    assert sdk is skill_sdk

    cli, _ = import_module_app("test_cli.py")
    import test_cli

    assert cli is test_cli


def test_run(debug_logging, mocker, monkeypatch):

    scaffold_path = pkg_resources.resource_filename(run.__name__, "scaffold")
    cwd = pathlib.Path(scaffold_path).absolute().__str__()
    if cwd not in sys.path:
        monkeypatch.syspath_prepend(cwd)

    uv = mocker.patch.object(run, "uvicorn")
    _, app = import_module_app(APP)
    assert list(app.intents.keys()) == ["SMALLTALK__GREETINGS"]

    run.execute(Namespace(module=APP))
    uv.run.assert_called_once_with(app, port=4242)


def test_develop(debug_logging, mocker, monkeypatch):

    scaffold_path = pkg_resources.resource_filename(develop.__name__, "scaffold")
    cwd = pathlib.Path(scaffold_path).absolute().__str__()
    if cwd not in sys.path:
        monkeypatch.syspath_prepend(cwd)

    uv = mocker.patch.object(develop, "uvicorn")

    #
    # In the previous test `app` object was _closed_
    # so we have to force reload the submodules to return
    # previously deleted static intent handlers
    #
    _, app = import_module_app(APP, reload=True)

    assert list(app.intents.keys()) == ["SMALLTALK__GREETINGS"]

    develop.execute(Namespace(module=APP))
    uv.run.assert_called_once_with(APP, reload=True, port=4242)


def test_init(tmpdir):

    init.execute(Namespace(out=tmpdir))

    required_files = [
        "impl/hello.py",
        "locale/de.po",
        "locale/en.po",
        "locale/fr.po",
        "scripts/develop",
        "scripts/run",
        "scripts/test",
        "scripts/version",
        "tests/test_hello.py",
        "app.py",
        "Dockerfile",
        "README.md",
        "requirements.txt",
        "skill.conf",
    ]
    assert all((pathlib.Path(tmpdir) / file).exists() for file in required_files)


def test_version(capsys: CaptureFixture, mocker):
    from skill_sdk import config

    scaffold_path = pkg_resources.resource_filename(develop.__name__, "scaffold")
    skill_conf = str(pathlib.Path(scaffold_path) / "skill.conf")
    mocker.patch.object(config, "get_skill_config_file", return_value=skill_conf)

    version.execute()

    out = capsys.readouterr()
    assert "0.1" in out.out


@pytest.fixture
def change_dir(request):
    """Fixture: set current dir to the path of `scaffold` project, and revert after the test"""

    scaffold_path = pkg_resources.resource_filename(init.__name__, "scaffold")
    os.chdir(scaffold_path)
    yield
    os.chdir(request.config.invocation_dir)


def test_scaffold(change_dir):
    """Run scaffold project testing suite"""

    _, app = import_module_app("app:app", reload=True)

    response = run_until_complete(app.test_intent("SMALLTALK__GREETINGS"))
    assert response.text == "HELLOAPP_HELLO"

    pytest.main(["tests"])
