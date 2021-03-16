#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

#
# "version" CLI command
#

import argparse
import logging


def execute(*args):
    """Print skill version"""

    from skill_sdk import config, log

    log.setup_logging(logging.ERROR, config.FormatType.HUMAN)

    config = config.init_config(config.get_skill_config_file())
    print(f"{config.get('skill', 'version')}")


def add_subparser(subparsers):

    version_parser = subparsers.add_parser(
        "version",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Print skill version and exit.",
    )
    version_parser.set_defaults(command=execute)
