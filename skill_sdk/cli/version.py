#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

"""CLI: "version" command"""

#
# Simply outputs the skill version as specified in config files:
#
#   this command is used in internal GitLab pipelines
#   to generate docker image name for the skill
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
    """
    Command arguments parser

    :param subparsers:
    :return:
    """

    version_parser = subparsers.add_parser(
        "version",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Print skill version and exit.",
    )
    version_parser.set_defaults(command=execute)
