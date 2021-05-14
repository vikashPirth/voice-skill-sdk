#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

"""CLI: "develop" command"""

#
#   - starts skill-designer
#   - starts skill in development mode
#   - displays skill logs in "Test -> log output"
#   - modifies Python sources in "Design"
#

import argparse
import logging
from contextlib import closing

from uvicorn import Config, Server

from skill_sdk.cli import import_module_app

logger = logging.getLogger(__name__)


def execute(arguments):
    """
    Run the app in "development" mode:

        set logging level to DEBUG
        logging format to human-readable
        override debug flag from configuration
        initialize Designer UI

    :param arguments:
    :return:
    """
    from skill_sdk import config, log, Skill
    from skill_sdk.cli.reloader import ThreadReload

    log.setup_logging(logging.DEBUG, config.FormatType.HUMAN)
    config.settings.SKILL_DEBUG = True

    with closing(Skill):

        while True:
            _, app = import_module_app(arguments.module)

            logger.info("Loaded app: %s", repr(app))
            logger.info("Loaded handlers: %s", list(app.intents))

            run_config = config.settings.http_config()

            logger.info("Starting app with config: %s", repr(run_config))

            config = Config(app.develop(), loop="asyncio", **run_config)

            server = Server(config=config)
            sock = config.bind_socket()
            supervisor = ThreadReload(config, target=server.run, sockets=[sock])
            supervisor.run()


def add_subparser(subparsers):
    """
    Command arguments parser

    :param subparsers:
    :return:
    """

    run_parser = subparsers.add_parser(
        "develop",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Starts the skill in development mode.",
    )
    run_parser.add_argument("module", help="Run module", nargs="?", default="impl")
    run_parser.set_defaults(command=execute)
