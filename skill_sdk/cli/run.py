#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

#
# "run" CLI command
#

import argparse
import logging
import uvicorn

from skill_sdk.cli import import_module_app


def execute(arguments):
    """
    Initialize and run the app with "uvicorn" server

    @return:
    """
    from skill_sdk import config, log, skill

    log.setup_logging()

    module, app = import_module_app(arguments.module)
    if app is None:
        app = skill.init_app()

    if not app.intents:
        raise RuntimeError(
            "No intent handlers loaded. Check the log messages for import errors..."
        )

    logging.info("Loaded handlers: %s", list(app.intents))

    run_config = config.settings.http_config()

    logging.info("Starting %s", repr(app))

    uvicorn.run(app, **run_config)


def add_subparser(subparsers):

    run_parser = subparsers.add_parser(
        "run",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Starts the skill in production mode.",
        description="Run the HTTP server as configured to handle requests.",
    )
    run_parser.add_argument("module", help="Run module", nargs="?", default="impl")
    run_parser.set_defaults(command=execute)
