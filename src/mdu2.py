#!/usr/local/bin/python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from core.extract2 import EBCDICProcess
from core.log import Log
from core.cli import CommandLine
import core.extract as Extract
from core.parsecp2 import EBCDICParser

import sys


def main(arg):

    cli = CommandLine()

    log = Log(cli.verbose)

    if cli.args.function == "extract":
        EBCDICProcess(log, cli.args, output_separator='\x7F').process()
    elif cli.args.function == "parse":
        EBCDICParser().run_parse(log, cli.args)
    elif cli.args.function == "both":
        EBCDICParser().run_parse(log, cli.args)
        EBCDICProcess(log, cli.args, output_separator='\x7F').process()
    else:
        log.Write(["not implemented yet"])

    log.Finish()


if __name__ == "__main__":
    main(sys.argv)
