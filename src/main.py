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

def _init_cli():
    cli = CommandLine()
    print('CLI arguments', vars(cli.args))
    print(cli)
    print(cli.verbose)
    log = Log(cli.verbose)
    return cli, log

def main(request, arg):
    print(arg)
    if len(arg) == 1:
        params = request.get_json()
        verbose = params.get('verbose', False)
        log = Log(verbose)
    else:
        cli, log = _init_cli()
        params = vars(cli.args)

    param = EBCDICParser().run_parse(params)
    EBCDICProcess(log, params, output_separator=',').process()
    # EBCDICProcess(log, params, output_separator='\x7F').process()

    log.Finish()


if __name__ == "__main__":
    # _init_cli()
    main({}, sys.argv)
