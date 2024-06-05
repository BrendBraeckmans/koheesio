"""Read from a location using Databricks' `autoloader`

Autoloader can ingest JSON, CSV, PARQUET, AVRO, ORC, TEXT, and BINARYFILE file formats.
"""

import json
from typing import Dict, Optional, Union
from enum import Enum
from pathlib import Path

from pyspark.sql.streaming import DataStreamReader
from pyspark.sql.types import StructType

from koheesio.models import Field, field_validator
from koheesio.spark.readers import Reader


class AutoLoaderFormat(Enum):
    """The file format, used in `cloudFiles.format`
    Autoloader supports JSON, CSV, PARQUET, AVRO, ORC, TEXT, and BINARYFILE file formats.
    """

    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    AVRO = "avro"
    ORC = "orc"
    TEXT = "text"
    BINARYFILE = "binaryfile"


class AutoLoader(Reader):
    """Read from a location using Databricks' `autoloader`

    Autoloader can ingest JSON, CSV, PARQUET, AVRO, ORC, TEXT, and BINARYFILE file formats.

    Notes
    -----
    `autoloader` is a `Spark Structured Streaming` function!

    Although most transformations are compatible with `Spark Structured Streaming`, not all of them are. As a result,
    be mindful with your downstream transformations.

    Parameters
    ----------
    format : Union[str, AutoLoaderFormat]
        The file format, used in `cloudFiles.format`. Autoloader supports JSON, CSV, PARQUET, AVRO, ORC, TEXT, and
        BINARYFILE file formats.
    location : str
        The location where the files are located, used in `cloudFiles.location`
    schema_location : str
        The location for storing inferred schema and supporting schema evolution, used in `cloudFiles.schemaLocation`.
    options : Optional[Dict[str, str]], optional, default={}
        Extra inputs to provide to the autoloader. For a full list of inputs, see
        https://docs.databricks.com/ingestion/auto-loader/options.html


    Example
    -------
    ```python
    from koheesio.steps.readers.databricks import AutoLoader, AutoLoaderFormat

    result_df = AutoLoader(
        format=AutoLoaderFormat.JSON,
        location="some_s3_path",
        schema_location="other_s3_path",
        options={"multiLine": "true"},
    ).read()
    ```

    See Also
    --------
    Some other useful documentation:

    - autoloader: https://docs.databricks.com/ingestion/auto-loader/index.html
    - Spark Structured Streaming: https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html
    """

    format: Union[str, AutoLoaderFormat] = Field(default=..., description=AutoLoaderFormat.__doc__)
    location: str = Field(
        default=...,
        description="The location where the files are located, used in `cloudFiles.location`",
    )
    schema_location: str = Field(
        default=...,
        alias="schemaLocation",
        description="The location for storing inferred schema and supporting schema evolution, "
        "used in `cloudFiles.schemaLocation`.",
    )
    options: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Extra inputs to provide to the autoloader. For a full list of inputs, "
        "see https://docs.databricks.com/ingestion/auto-loader/options.html",
    )
    schema: Optional[Union[Path, str, StructType]] = Field(
        default=None,
        description="Explicit schema to infer the schema of the input files.",
    )

    @field_validator("format")
    def validate_format(cls, format_specified):
        """Validate `format` value"""
        if isinstance(format_specified, str):
            if format_specified.upper() in [f.value.upper() for f in AutoLoaderFormat]:
                format_specified = getattr(AutoLoaderFormat, format_specified.upper())
        return str(format_specified.value)

    @field_validator("schema")
    def validate_schema(cls, schema_specified):
        """Validate `schema` value"""
        schema = schema_specified
        if isinstance(schema, StructType):
            return schema

        if schema is not None:
            schema_path = Path(schema)
            if schema_path.exists():
                schema = schema_path.read_text()
            else:
                raise FileNotFoundError(f"Schema file not found at path {schema}")
            schema = StructType.fromJson(json.loads(schema))
        return schema

    def get_options(self):
        """Get the options for the autoloader"""
        self.options.update(
            {
                "cloudFiles.format": self.format,
                "cloudFiles.schemaLocation": self.schema_location,
            }
        )
        return self.options

    # @property
    def reader(self) -> DataStreamReader:
        reader = self.spark.readStream.format("cloudFiles")
        if self.schema is not None:
            reader = reader.schema(self.schema)
        reader = reader.options(**self.get_options())
        return reader

    def execute(self):
        """Reads from the given location with the given options using Autoloader"""
        self.output.df = self.reader().load(self.location)
