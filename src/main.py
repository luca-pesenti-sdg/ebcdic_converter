#!/usr/local/bin/python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from core.extract import EBCDICProcess
from core.log import Log
from core.cli import CommandLine
import core.extract as Extract
from core.parquet import FileHandler
from core.parsecp import EBCDICParser

import sys

SEPARATOR = "\x7F"

def _init_cli():
    cli = CommandLine()
    print("CLI arguments", vars(cli.args))
    log = Log(cli.verbose)
    return cli, log


def main(request, arg):
    if len(arg) == 1:
        params = request.get_json()
        verbose = params.get("verbose", False)
        log = Log(verbose)
    else:
        cli, log = _init_cli()
        params = vars(cli.args)

    json_copy = EBCDICParser().run_parse(params)
    EBCDICProcess(log, params, output_separator=SEPARATOR).process()
    FileHandler(
        logger=log, path_to_file=params["output"], output_separator=SEPARATOR
    ).to_parquet(json_schema=json_copy)

    log.Finish()


if __name__ == "__main__":
    # HOW TO RUN
    # python3 src/main.py both path/to/copybook outpath/copybook/json -input path/to/ebcdic -output path/to/parquet/result -print 10000 -verbose true
    main({}, sys.argv)
