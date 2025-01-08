#!/usr/local/bin/python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from core.extract import EBCDICProcess
from core.log import Log
from core.cli import CommandLine
import core.extract as Extract
from core.parsecp import EBCDICParser

import sys

# TODO: switch CLI with config

def main(arg):

    cli = CommandLine()

    log = Log(cli.verbose)

    param = EBCDICParser().run_parse(log, cli.args)
    EBCDICProcess(log, cli.args, output_separator='\x7F').process()

    log.Finish()


if __name__ == "__main__":
    main(sys.argv)
