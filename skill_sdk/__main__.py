#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

#
# Command line interface
#

import sys
import argparse
import logging

from skill_sdk.cli import (
    add_logging_options,
    init,
    develop,
    run,
    translate,
    version,
)
from skill_sdk import config, log


def main() -> None:
    """CLI - run as a standalone python app"""

    parser = argparse.ArgumentParser(
        prog="vs",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Magenta Voice Skill CLI. 'vs' command is a helper that "
        "allows you to run several Magenta skill tasks: "
        "initialize skill project, define or test your intent handlers.",
    )

    add_logging_options(parser)
    subparsers = parser.add_subparsers(dest="command", help="Skill commands")
    init.add_subparser(subparsers)
    run.add_subparser(subparsers)
    develop.add_subparser(subparsers)
    translate.add_subparser(subparsers)
    version.add_subparser(subparsers)

    arguments = parser.parse_args()
    log.setup_logging(
        arguments.loglevel or logging.WARNING,
        log_format=config.FormatType.HUMAN,
    )

    if getattr(arguments, "command", None):
        arguments.command(arguments)

    else:
        # Print usage
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
