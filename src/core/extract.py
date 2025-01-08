# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from io import BufferedReader, TextIOWrapper
import multiprocessing as mp
from typing import List, Union
from core.ebcdic import EBCDICDecoder
from core.filemeta import FileMetaData
from core.ebcdic import unpack
from itertools import cycle
from pathlib import Path
import argparse
from core.log import Log


class EBCDICProcess:

    def __init__(self, logger: Log, extra_args: argparse.Namespace, output_separator: str = None):
        self._logger = logger
        self._extra_args = extra_args

        # The following remapping is done to make the code more readable but could be avoided
        self._metadata_file = FileMetaData(self._logger, self._extra_args)
        self._input_file = self._metadata_file.general["input"]
        self._output_type = self._metadata_file.general["output_type"]
        self._output = self._metadata_file.general["output"]
        self._working_folder = self._metadata_file.general["working_folder"]
        self._input_type = self._metadata_file.inputtype
        self._threads = self._metadata_file.general["threads"]
        self._print = self._metadata_file.general["print"]
        self._skip = self._metadata_file.general["skip"]
        self._part_k_name = self._metadata_file.general["part_k_name"]
        self._sort_k_name = self._metadata_file.general["sort_k_name"]
        self._rem_low_values = self._metadata_file.general["rem_low_values"]
        self._output_separator = self._metadata_file.general["output_separator"] if not output_separator else output_separator
        self._req_size = self._metadata_file.general["req_size"]
        self._verbose = self._metadata_file.general["verbose"]
        self._max = self._metadata_file.general["max"]
        # Expressed in bytes
        self._record_length = self._metadata_file.general["input_recl"]

        # NOTE: I'm not sure about the name
        self._record_format = self._metadata_file.general["input_recfm"]

        # S3 related
        self._output_s3 = self._metadata_file.general["output_s3"]
        self._input_s3_url = self._metadata_file.general["input_s3"]

        # NOTE: originally it was s3-obj but I think it was a typo since it is written everywhere else as s3_obj
        self._output_record = (
            [] if self._output_type in ["file", "s3_obj", "s3"] else {}
        )

        # returns True if threads == 1
        self._single_thread = self._metadata_file.general["threads"] == 1

        # NOTE: Extend here to handle other file location
        self._input_obj_map = {
            "s3": self._get_s3_file_obj,
            "s3_url": self._get_s3_file_obj,
            "local": self._get_local_file_obj,
        }

    def _write_output(
        self,
        output_file: Union[TextIOWrapper, List],
        record: bytes,
        new_line: str,
    ) -> bool:
        output_record = [] if self._output_type in ["file", "s3-obj", "s3"] else {}
        layout = self._metadata_file.Layout(record)
        if layout != "discard":
            for transf in self._metadata_file.general[layout]:
                # print(record[transf["offset"] : transf["offset"] + transf["bytes"]])
                self._add_field(
                    output_record=output_record,
                    id=transf["name"],
                    type=transf["type"],
                    partkey=transf["part-key"],
                    sortkey=transf["sort-key"],
                    value=EBCDICDecoder(
                        bytes=record[
                            transf["offset"] : transf["offset"] + transf["bytes"]
                        ],
                        type=transf["type"],
                        dec_places=transf["dplaces"],
                        rem_lv=self._rem_low_values,
                        rem_spaces=False,
                    ).unpack(),
                    add_empty=False,  # seems useless
                )
            if self._output_type in ["file", "s3_obj", "s3"]:
                output_file.write(new_line + self._output_separator.join(output_record))

            # This can be removed, since we only use local files, but is kept for clarity
            else:
                output_file.append({"PutRequest": {"Item": output_record}})

                if len(output_file) >= self._req_size:
                    self._logger.Write(["Writing batch to DynamoDB"])
                    self._write_to_dynamodb()
                    output_file.clear()
            return True
        return False

    def _add_field(
        self, output_record, id, type, partkey, sortkey, value, add_empty: bool = False
    ):
        if self._output_type in ["file", "s3-obj", "s3"]:
            output_record.append(value)
        else:
            if not partkey and not sortkey:
                if value != "" or add_empty:
                    output_record[id.replace("-", "_")] = {}
                    output_record[id.replace("-", "_")][
                        "S" if type == "ch" else "N"
                    ] = value
            elif not partkey:
                if self._sort_k_name in output_record:
                    output_record[self._sort_k_name]["S"] = (
                        self._output_record[self._sort_k_name]["S"] + "|" + value
                    )
                else:
                    output_record[self._sort_k_name] = {}
                    output_record[self._sort_k_name]["S"] = value
            else:
                if self._part_k_name in output_record:
                    output_record[self._part_k_name]["S"] = (
                        output_record[self._part_k_name]["S"] + "|" + value
                    )
                else:
                    output_record[self._part_k_name] = {}
                    output_record[self._part_k_name]["S"] = value

    # region CORE METHODS

    def process(self):
        if self._single_thread:
            output_file = self._generate_outfile_single_thread()
            self._process_single_thread(output_file)
        else:
            output_files = self._generate_outfile_multi_thread()
            self._process_multi_thread(output_files)

    def _get_local_file_obj(self) -> BufferedReader:
        return open(self._input_file, "rb")

    def _get_s3_file_obj(self) -> None:
        self._logger.Write(["EBCDICProcess: s3 not implemented yet"])
        return None

    def _get_s3_url_file_obj(self) -> None:
        self._logger.Write(["EBCDICProcess: s3_url not implemented yet"])
        return None

    def _getRDW(b: bytearray):
        return int("0x" + b[:2].hex(), 0) - 4 if len(b) > 0 else 0

    def _read(self, input):
        if self._record_format == "fb":
            print(input)
            return input.read(self._record_length)
        else:
            l = self._getRDW(input.read(4))
            print(l)
            return input.read(l)

    # endregion

    # region SINGLE THREADED METHODS
    def _generate_outfile_single_thread(
        self,
    ) -> Union[TextIOWrapper, List]:
        self._logger.Write(["EBCDICProcess: single-threaded processing selected"])

        if self._output_type in ["file", "s3_obj", "s3"]:
            self._logger.Write(
                ["Creating output file", self._working_folder, self._output]
            )
            folder = Path(self._working_folder + self._output).parent

            Path(folder).mkdir(parents=True, exist_ok=True)

            return open(self._working_folder + self._output, "w")
        else:
            return []

    def _process_single_thread(self, output_file: Union[TextIOWrapper, List]):
        self._logger.Write(["EBCDICProcess: single-threaded processing selected"])
        index = 0
        new_line = ""
        input_file = self._input_obj_map[self._input_type]()
        while index < self._max or self._max == 0:
            record = self._read(input_file)
            print(record)
            if not record:
                break
            index += 1
            if index > self._skip:
                if self._print != 0 and index % self._print == 0:
                    self._logger.Write(["Records read", str(index)])
                r = self._write_output(output_file, record, new_line=new_line)
                if r:
                    new_line = "\n"
        self._logger.Write(["Records processed", str(index)])

    # endregion

    # region MULTI THREADED METHODS
    def _generate_outfile_multi_thread(self) -> List:
        self._logger.Write(["EBCDICProcess: multi-threaded processing selected"])
        file_list = []
        for thread_number in range(1, self._threads + 1):
            outfile_name = (
                self._working_folder + self._output + "." + str(thread_number)
            )
            file_list.append(outfile_name)

        return file_list

    def _queue_worker(self, out_ds, queue_dict: dict, suffix: str = ""):

        if self._output_type in ["file", "s3_obj", "s3"]:
            outfile = open(out_ds, "w")
        else:
            outfile = []

        new_line = ""

        while True:
            record = queue_dict.get()

            if record is not None:
                r = self._write_output(outfile, record, new_line)
                if r:
                    new_line = "\n"
            else:
                self._logger.Write(["Closing output", self._output, "thread", suffix])
                self._close_output(outfile=outfile, out_ds=out_ds, suffix=suffix)
                break

    def _process_multi_thread(self, output_files: List):
        self._logger.Write(["EBCDICProcess: multi-threaded processing selected"])

        queue_dict = {}
        process_list = []

        for file in output_files:
            queue_dict[file] = mp.Queue()
            process = mp.Process(
                target=self._queue_worker,
                args=(file, queue_dict[file], "." + file.split(".")[-1]),
            )
            process.start()
            process_list.append(process)

        index = 0
        while index < self._max or self._max == 0:
            record = self._read(self._input_obj_map[self._input_type]())
            cycle_files = cycle(process_list)
            next_queue = next(cycle_files)
            queue_dict[next_queue].put(record)

        for file in output_files:
            queue_dict[file].put(None)
        for process in process_list:
            process.join()

        self._logger.Write(["Records processed", str(index)])

    def _close_output(self, outfile, out_ds, suffix=""):

        if self._output_type in ["file", "s3_obj", "s3"]:
            outfile.close()
            if self._output_s3 != "":
                self._logger.Write(
                    ["Uploading to s3", self._output_s3, self._output + suffix]
                )
                if self._verbose:
                    self._logger.Write(["Source file", out_ds])
                # try:
                #     response = boto3.client('s3').upload_file(out_ds, fMetaData.general['output_s3'], fMetaData.general['output'] + suffix)
                # except ClientError as e:
                #     self._logger.Write(e)
            elif self._input_s3_url != "":
                self._logger.Write(["Generating s3 lambda object response"])
                # try/except missing
                # with open(out_ds, 'rb') as f:
                #     boto3.client('s3').write_get_object_response(Body=f,RequestRoute=fMetaData.general['input_s3_route'],RequestToken=fMetaData.general['input_s3_token'])
        else:
            if len(outfile) >= 0:
                self._write_to_dynamodb()

    # endregion

    def _write_to_dynamodb(self):
        self.logger.Write(["EBCDICProcess: Writing to DynamoDB is not implemented yet"])
        # Original code:
        # response = boto3.client('dynamodb').batch_write_item(RequestItems={ table : data })
