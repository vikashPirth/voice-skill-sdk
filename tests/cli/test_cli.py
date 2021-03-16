#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

import sys
import shutil
import pathlib
import pkg_resources
from argparse import Namespace
from contextlib import closing
from typing import Callable

import pytest
from pytest import CaptureFixture
from _pytest.pytester import Testdir, RunResult

from skill_sdk.cli import import_module_app, develop, init, run, version


@pytest.fixture
def run_with_stdin(testdir: Testdir) -> Callable[..., RunResult]:
    def do_run(*args, stdin):
        args = [shutil.which("vs")] + list(args)
        return testdir.run(*args, stdin=stdin)

    return do_run


def test_import_module_app():

    sdk, _ = import_module_app("skill_sdk")
    import skill_sdk

    assert sdk is skill_sdk

    cli, _ = import_module_app("test_cli.py")
    import test_cli

    assert cli is test_cli


def test_run(mocker, monkeypatch):

    scaffold_path = pkg_resources.resource_filename(run.__name__, "scaffold")
    cwd = pathlib.Path(scaffold_path).absolute().__str__()
    if cwd not in sys.path:
        monkeypatch.syspath_prepend(cwd)

    uv = mocker.patch.object(run, "uvicorn")
    _, app = import_module_app("app:app")

    with closing(app):
        run.execute(Namespace(module="app:app"))

    uv.run.assert_called_once_with(app, port=4242)


def test_develop(mocker, monkeypatch):

    scaffold_path = pkg_resources.resource_filename(develop.__name__, "scaffold")
    cwd = pathlib.Path(scaffold_path).absolute().__str__()
    if cwd not in sys.path:
        monkeypatch.syspath_prepend(cwd)

    uv = mocker.patch.object(develop, "uvicorn")
    _, app = import_module_app("app:app")
    with closing(app):
        develop.execute(Namespace(module="app:app"))

    uv.run.assert_called_once_with("app:app", reload=True, port=4242)


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
