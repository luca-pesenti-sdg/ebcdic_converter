import json
from typing import List, Tuple, Union
from core.log import Log
import pyarrow as pa
import traceback
import pyarrow.csv as pa_csv
import pyarrow.parquet as pa_parquet

data_type_mapping = {
    "ch": pa.string(),
    # "zd": pa.float64(),
    # "zd+": pa.float64(),
    # "bi": pa.float64(),
    # "bi+": pa.float64(),
    "dp": pa.float64(),
    "dp+": pa.float64(),
    # "pd": pa.float64(),
    # "pd+": pa.float64(),
}


class FileHandler:
    def __init__(self, logger: Log, path_to_file: str, output_separator: str):
        """Initialize the Parquet class.

        Parameters:
        -----------
        logger : Log
            Logger instance for logging messages.
        path_to_file : str
            Path to the file to be processed.
        output_separator : str
            Separator to be used in the output.

        """
        self._logger = logger
        self._path_to_file = path_to_file
        self._output_separator = output_separator

    def _clean_field(
        self, fields_name: str, chars_to_rm: List[Tuple[str, str]] = [("-", "_")]
    ) -> str:
        """Cleans the given field name by replacing specified characters.

        Parameters:
        -----------
        fields_name : str
            The name of the field to be cleaned.
        chars_to_rm : List[Tuple[str, str]], optional
            A list of tuples where each tuple contains a character to be replaced and the character to replace it with. Defaults to [("-", "_")].

        Returns:
        --------
        str
            The cleaned field name with specified characters replaced.
        """

        for char in chars_to_rm:
            fields_name = fields_name.replace(char[0], char[1])
        return fields_name

    def _extract_schema_from_json(
        self, json_schema: Union[str, dict], is_file: bool = False
    ) -> pa.schema:
        """Extracts a PyArrow schema from a JSON schema.

        Parameters:
        -----------
        json_schema : (Union[str, dict])
            The JSON schema, either as a string (file path) or a dictionary.
        is_file : (bool, optional), optional
            Flag indicating if `json_schema` is a file path. Defaults to False.

        Returns:
        -----------
            pa.schema: The corresponding PyArrow schema.

        Raises:
        -------
            FileNotFoundError: If `is_file` is True and the file does not exist.
            json.JSONDecodeError: If the JSON schema is not valid.
        """

        if is_file:
            with open(json_schema, "r") as f:
                json_data = json.load(f)
        else:
            json_data = json_schema

        fields = []
        for field in json_data.get("transf", []):
            field_name = self._clean_field(field["name"])
            data_type = data_type_mapping.get(
                field["type"], pa.decimal128(38, field["dplaces"])
            )
            fields.append((field_name, data_type))
        return pa.schema(fields)

    def to_parquet(
        self,
        schema: Union[pa.schema, List[Tuple[str, pa.DataType]]] = None,
        json_schema: Union[str, dict] = None,
    ):
        """Converts a CSV file to a Parquet file using the provided schema or JSON schema.

        Parameters:
        -----------
        schema : Union[pa.schema, List[Tuple[str, pa.DataType]]], optional
            The schema to use for the Parquet file. Can be a pyarrow schema or a list of tuples
            where each tuple contains a column name and its corresponding pyarrow data type.
        json_schema : Union[str, dict], optional
            The JSON schema to use for the Parquet file. Can be a JSON string or a dictionary.

        Raises:
        -------
        Exception
            If neither schema nor json_schema is provided.
            If the provided schema is not a list or pa.schema.

        Notes:
        ------
        If both schema and json_schema are provided, the schema will take precedence.
        The method logs the conversion process and writes the Parquet file to the same
        directory as the CSV file, replacing the .csv extension with .parquet.
        """

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
        # try:
        csv = pa_csv.read_csv(
            self._path_to_file,
            read_options=pa_csv.ReadOptions(column_names=schema.names),
            convert_options=pa_csv.ConvertOptions(
                column_types=schema,
                strings_can_be_null=True,
                # INFO: https://arrow.apache.org/docs/python/generated/pyarrow.csv.ConvertOptions.html#pyarrow.csv.ConvertOptions
            ),
            parse_options=pa_csv.ParseOptions(delimiter=self._output_separator,quote_char=False,),
        )
        print(csv.schema)
        pa_parquet.write_table(
            csv, self._path_to_file.replace(".csv", ".parquet"), version="2.6"
        )
        print(f"\33[92mParquet file saved to {self._path_to_file.replace('.csv', '.parquet')}\33[0m")
        
        # For local test only
        # except Exception as e:
        #     print(f"\33[91mParquet file {self._path_to_file.replace('.csv', '.parquet')} raised the following error")
        #     traceback.print_exc()
        #     print("\33[0m")

