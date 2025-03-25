"""
Ingest CSV file

Since CSV doesnt have datatypes built in we can use Pydantic to
coerce the data into types


For dataframes we use pandantic
"""

import csv

from typing import Annotated
from pydantic import BaseModel, BeforeValidator, Field, field_validator
from pandantic import Pandantic

import pandas as pd

CSV_FILE_PATH_1 = "./data/test.csv"
CSV_FILE_PATH_2 = "./data/test2.csv"

# JSON
csv_data = []
# with open(CSV_FILE_PATH_1) as f:
#     csv_data = csv.reader(f)
#     for lines in csv_data:
#         # print(lines)
#         pass


def name_int(value: str):
    try:
        return int(value.strip().replace(",", "").replace("\t", ""))
    except Exception as ex:
        raise ValueError(f"data could be parsed into a valid integer {str(ex)}")


IntChecker = Annotated[int, BeforeValidator(name_int)]


class Estimate(BaseModel):
    area: str
    july_1_2001: IntChecker
    july_1_2000: IntChecker
    april_1_2000: IntChecker


def validate_estimates(path: str):
    with open(path) as f:
        data = csv.DictReader(
            f, fieldnames=["area", "july_1_2001", "july_1_2000", "april_1_2000"]
        )
        next(data)  # skip header row
        for row in data:
            yield Estimate.model_validate(row)


estimates = validate_estimates(CSV_FILE_PATH_1)

data = list(estimates)
print(data[0])


# Pandas


class DataFrameSchema(BaseModel):
    """Example schema for testing."""

    field_bool: bool = Field(alias="fieldBool")
    field_str: str = Field(alias="fieldStr")
    field_int: int = Field(alias="fieldInt")
    field_float: float = Field(alias="fieldFloat")

    @field_validator("field_int")
    def must_be_even(cls, value: int) -> int:
        if value % 2 != 0:
            raise ValueError("Number must be even")
        return value


validator = Pandantic(schema=DataFrameSchema)

df = pd.read_csv(CSV_FILE_PATH_2, sep="\t")
# print(df.head())
try:
    validator.validate(dataframe=df, errors="raise")
except ValueError as e:
    print(str(e))
