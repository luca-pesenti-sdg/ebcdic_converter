import json
from typing import List, Tuple, Union
from core.log import Log
import pandas as pd
import pyarrow as pa
import pyarrow.csv as pa_csv
import pyarrow.parquet as pa_parquet

data_type_mapping = {
    "ch": pa.string(),
    "zd": pa.float16(),
    "zd+": pa.float16(),
    "bi": pa.float16(),
    "bi+": pa.float16(),
    "dp": pa.float16(),
    "dp+": pa.float16(),
    "pd": pa.float16(),
    "pd+": pa.float16(),
}


class FileHandler:
    def __init__(self, logger: Log, path_to_file: str, output_separator: str):
        self._logger = logger
        self._path_to_file = path_to_file
        self._output_separator = output_separator

    def _clean_field(
        self, fields_name: str, chars_to_rm: List[Tuple[str, str]] = [("-", "_")]
    ) -> str:
        """
        Rename headers of the dataframe
        """
        for char in chars_to_rm:
            fields_name = fields_name.replace(char[0], char[1])
        return fields_name

    def _extract_schema_from_json(
        self, json_schema: Union[str, dict], is_file: bool = False
    ) -> pa.schema:
        """
        Extract schema from JSON file
        """
        if is_file:
            with open(json_schema, "r") as f:
                json_data = json.load(f)
        else:
            json_data = json_schema

        fields = []
        for field in json_data.get("transf", []):
            field_name = self._clean_field(field["name"])
            fields.append((field_name, data_type_mapping[field["type"]]))
        return pa.schema(fields)

    def to_parquet(
        self,
        schema: Union[pa.schema, List[Tuple[str, pa.DataType]]] = None,
        json_schema: Union[str, dict] = None,
    ):
        self._logger.Write(["EBCDICProcess: Converting from csv to parquet"])

        if not schema and not json_schema:
            raise Exception("Either schema or json_schema must be provided")

        if not schema:
            if isinstance(json_schema, str):
                schema = self._extract_schema_from_json(
                    json_schema=json_schema, is_file=True
                )
            else:
                schema = self._extract_schema_from_json(
                    json_schema=json_schema, is_file=False
                )
        elif isinstance(schema, pa.schema):
            pass
        elif isinstance(schema, list):
            schema = pa.schema(schema)
        else:
            raise Exception("Schema must be a list or pa.schema")

        csv = pa_csv.read_csv(
            self._path_to_file,
            read_options=pa_csv.ReadOptions(column_names=schema.names),
            convert_options=pa_csv.ConvertOptions(
                strings_can_be_null=True,
            ),
            parse_options=pa_csv.ParseOptions(delimiter=self._output_separator),
        )
        pa_parquet.write_table(csv, self._path_to_file.replace(".csv", ".parquet"))
