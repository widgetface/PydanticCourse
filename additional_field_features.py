""" """

from uuid import uuid4
from enum import Enum
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    UUID4,
)
from pydantic.alias_generators import to_camel
from datetime import date, datetime, UTC


# using different Field atributes
class Example(BaseModel):
    num: float = Field(gt=2, le=10, multiple_of=2)
    name: str = Field(min_length=2, max_length=10)  # Like conlist
    tup: tuple[int, ...]  # Te dots mean a tuple of length 1 or more
    # If you put tuple[int] it would mean tuple OF ONE int and fail if > 1 int
    regex_field: str = Field(pattern="^[0-9]{5}-[0-9]{4}$")  # Use regex


# Default Factories
# @dataclass uses default factory to make a deep copy of mutable defaults
# Like list [] to avoid the same one being used over in diferent icnatnces

# WRONG WAY
# class Log(BaseModel):
#     date_: datetime = datetime.now(UTC) # Here this is mutable every instance ill use the
#     # datatime hen its first initiated


# RIGHT WAY
# Field(default_factory= lambda: datetime.now(UTC)) REQUIRES A FUNCTION use lambda
class Log(BaseModel):
    date_: datetime = Field(default_factory=lambda: datetime.now(UTC))
    elements: list[int] = Field(
        default_factory=lambda: []
    )  #  elements: list[int] = []  works here as well here


# Additional Field constraints
# Here there's no type coercion on all fields
class StrictAllFields(BaseModel):
    model_config = ConfigDict(strict=True)  # False by default
    a: bool = True
    b: bool = True


class StrictAtFieldLevel(BaseModel):
    a: bool = Field(strict=True)  # a is strict no type coercion
    b: bool = False  # now b is not strict so set b=1.0 coerced to True


# You can freeze whole model
# model_config = ConfigDict(frozen=True)
# Here just on a field you cannot use above (freeze whole model)
# and opt out at field level
class FrozenField(BaseModel):
    a: int = Field(default=10, frozen=True)


# Exclude fields (perhaps a secret value)
class ExcludeField(BaseModel):
    secret: str = Field(exclude=True)
    api_token: str = Field(exclude=True)
    name: str | None = None


# Example exclude fields
# The laternative is ex.model_dump(exclude=["secret". "api_token"])
# BUR YOU'D HAVE TO REMEMBER TO DO IT AND ITS FRAGILE BETTR DO AT FILED LEVEL
ex = ExcludeField(secret="QADSF546", api_token="gekuewiu", name="Janny")
print(ex.model_dump())


# PROJECT


class AutomobleType(Enum):
    sedan = "Sedan"
    coupe = "Coupe"
    convertible = "Convertible"
    suv = "SUV"
    sport = "Sport"


class Automobile(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_default=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        alias_generator=to_camel,
    )
    id_: UUID4 = Field(alias="id", default_factory=lambda: uuid4())
    manufacturer: str
    series_name: str
    type_: AutomobleType = Field(alias="type")
    is_electric: bool = False
    # manufactured_date not bfore 01/01/1980
    manufactured_date: date = Field(validation_alias="completionDate", ge=(1980, 1, 1))
    basic_msrp_usd: float = Field(
        validation_alias="msrpUSD", serialization_alias="baseMSRPUSD"
    )
    vin: str
    number_of_doors: int = Field(
        default=4, alias="doors", validation_alias="doors", min=2, max=4, multiple_of=2
    )
    reg_country: str | None = Field(
        default=None,
        alias="registrationCountry",
    )
    license_plate: str | None = Field(default=None, alias="licensePlate")

    # This is used to change format of manufactured_date
    # when_used="json-unless-none" apply only to json
    @field_serializer("manufactured_date", when_used="json-unless-none")
    def serialize_date(self, value: date) -> str:
        return value.strftime("%Y/%m/%d")
