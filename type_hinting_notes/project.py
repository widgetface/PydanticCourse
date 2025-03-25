from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from datetime import date


# class Automoile(BaseModel):
#     manufacturer: str
#     series_name: str
#     type_: str
#     is_electric: bool = False
#     manufactured_date: date
#     basic_msrp_usd: float
#     vin: str
#     number_of_doors: int = 4
#     reg_country: str | None = None
#     license_plate: str | None = None


# ConfigDict
# Bases: TypedDict
# A TypedDict for configuring Pydantic behaviour.
# See https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.title


# Examples
class User1(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(alias="full_name")
    age: int


user = User1(full_name="John Doe", age=20)
print(user)


# Whether models are faux-immutable, i.e. whether __setattr__ is allowed
class User2(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    age: int


try:
    user2 = User2(name="Ken", age=34)
    user2.age = 35

except ValidationError as e:
    # error   Instance is frozen [type=frozen_instance, input_value=35,
    print(e)


# allow - Allow any extra attributes.
# forbid - Forbid any extra attributes.
# ignore - Ignore any extra attributes.


class User3(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str


# try:
#     User3(name="John Doe", age=20)
# except ValidationError as e:
#     print(e)


# Enums
class SomeEnum(Enum):
    FOO = "foo"
    BAR = "bar"
    BAZ = "baz"


class SomeModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    some_enum: SomeEnum


model2 = SomeModel(some_enum=SomeEnum.BAR)
print(model2.model_dump())

# validate on field change


class User4(BaseModel, validate_assignment=True):
    name: str


user4 = User4(name="John Doe")
print(user)
# Fails validation hen field chnaged to int (should be str)
try:
    user.name = "Jonny Doe"  # 123
except ValidationError as e:
    print(e)


# Set strict mode
class Model(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str = "Tom"
    age: int = 10  # "wrong"


# Set default to be vaidated
class DefaultModel(BaseModel):
    model_config = ConfigDict(validate_default=True)

    name: str
    age: int


# See page https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.strict

# Apply ConfigDict to Automobile


class AutomobleType(Enum):
    sedan = "Sedan"
    coupe = "Coupe"
    convertable = "Convertable"
    suv = "SUV"
    sport = "Sport"


class Automoile(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_default=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )
    manufacturer: str
    series_name: str
    type_: AutomobleType
    is_electric: bool = False
    manufactured_date: date
    basic_msrp_usd: float
    vin: str
    number_of_doors: int = 4
    reg_country: str | None = None
    license_plate: str | None = None


print(Automoile.model_config)


# Field Alias

