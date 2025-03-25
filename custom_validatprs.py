from uuid import uuid4
from pprint import pp
import pytz
from enum import Enum
import collections.abc
from typing import Annotated, get_args, TypeVar
from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    computed_field,
    ConfigDict,
    Field,
    StringConstraints,
    field_serializer,
    field_validator,
    UUID4,
    ValidationInfo,
)
from pydantic.alias_generators import to_camel
from datetime import date, datetime
from dateutil.parser import parse


# Custom validators are functions
# Can validate before or after Pydantic validation
# Can transform values input -> output
# Multiple validators on the same field

# After validators


class SimpleExample(BaseModel):
    num: int = Field(gt=0, lt=10)

    # Correct use of @field_validator as a class method
    @field_validator("num")
    @classmethod
    def simple_validator(cls, value: int) -> int:
        print("in validator")
        if value % 2 == 0:
            return value
        raise ValueError("value is odd")


# n = SimpleExample(num=3)
m = SimpleExample(num=4)


# def make_utc(dt: datetime) -> datetime:
#     if dt.tzinfo is None:
#         dt = pytz.utc.localize(dt)
#     else:
#         dt = dt.astimezone(pytz.utc)
#     return dt


class TimeModel(BaseModel):
    dt: datetime

    # Correctly using @field_validator for a class method
    @field_validator("dt")
    @classmethod  # the method receives the class (cls) as its first argument, rather than an instance (self).
    def make_utc(cls, dt: datetime) -> datetime:
        # Ensure the datetime is timezone-aware
        if dt.tzinfo is None:
            # If naive, localize it to UTC
            dt = pytz.utc.localize(dt)
        else:
            # Otherwise, convert to UTC if already timezone-aware
            dt = dt.astimezone(pytz.utc)
        return dt


# Example usage
m = TimeModel(dt="2020-01-01")
print(m.dt)  # This should print the datetime in UTC


class CostModel(BaseModel):
    unit_cost: float
    unit_price: float

    @field_validator("unit_cost", "unit_price")  # or  @field_validator("*")
    @classmethod
    def round_2(cls, value: float) -> float:
        return round(value, 2)

    @computed_field
    @property
    def total_cost(self) -> float:
        return self.unit_cost + self.unit_price


cc = CostModel(unit_cost=2.666, unit_price=3.099)
print(cc)


# Before validators
# Usually bvalidators runafter Pydantic validation ,
#  becuase value is guarenteed to be Pydantic valid
# You might want to format a datetime string to ensure Pydantic can handle it


# good = CheckDateTimeModel(dt=datetime('2020, 1, 1, 12, 0'))
# bad = CheckDateTimeModel(dt=datetime('2020/1/1)
# Pydantic cannot hanle string in bad itll throw invaid error
# So to accept certain datetime formats we have to intercept the value before Pydantic
# See above


class CheckDateTimeModel(BaseModel):
    dt: datetime

    @field_validator("dt", mode="before")
    @classmethod
    def parse_datetime(cls, value: str) -> str:
        if isinstance(value, str):
            try:
                return parse(value)
            except Exception as e:
                raise ValueError(str(e))
        return value


print(CheckDateTimeModel(dt="2020/1/1 5pm"))
# print(CheckDateTimeModel(dt="mystring"))
# Validators using Annotated


def parse_datetime(cls, value: str) -> str:
    if isinstance(value, str):
        try:
            return parse(value)
        except Exception as e:
            raise ValueError(str(e))
    return value


# DateTime = Annotated[datetime, BeforeValidator(parse_datetime)]


# class AnnotatedCheckDateTime(BaseModel):
#     dt: DateTime


# adt = AnnotatedCheckDateTime(dt="2020/2/1 8pm")
# print(adt)

# Dependent Field Validation
# Custom validators can receive an argument for another attribute


class DependencyModel(BaseModel):
    a: int
    b: list[int]
    c: str
    d: str

    @field_validator("c")
    @classmethod
    def validator(cls, value: str, validated_values: ValidationInfo) -> str:
        print(f"validator value = {value}")
        print(f"validator validatedValues = {validated_values}")
        print(f"validator validatedValues data = {validated_values.data}")

        return f"list is {len(validated_values.data['b'])}"


d = DependencyModel(a=1, b=[1, 2, 3], c="hello", d="goodbye")
print(d)
# We don't see attribute 'd' as 'c' IS BEFORE 'd' validations done in top down order
# You could use the above to check one timestamp is before another
# e.g. strat_date and end_date
# or a discount is applied to a price etc.

# PROJECT
countries = {
    "australia": ("Australia", "AUS"),
    "canada": ("Canada", "CAN"),
    "china": ("China", "CHN"),
    "france": ("France", "FRA"),
    "germany": ("Germany", "DEU"),
    "india": ("India", "IND"),
    "mexico": ("Mexico", "MEX"),
    "norway": ("Norway", "NOR"),
    "pakistan": ("Pakistan", "PAK"),
    "san marino": ("San Marino", "SMR"),
    "sanmarino": ("San Marino", "SMR"),
    "spain": ("Spain", "ESP"),
    "sweden": ("Sweden", "SWE"),
    "united kingdom": ("United Kingdom", "GBR"),
    "uk": ("United Kingdom", "GBR"),
    "great britain": ("United Kingdom", "GBR"),
    "britain": ("United Kingdom", "GBR"),
    "us": ("United States of America", "USA"),
    "united states": ("United States of America", "USA"),
    "usa": ("United States of America", "USA"),
}

valid_country_names = sorted(countries.keys())


def lookup_country(name: str) -> tuple[str, str]:
    name = name.strip().casefold()
    # casefold = Want to do case-insensitive string comparison? Use .casefold().
    # Note casefold is "similar to lowercasing but more aggressive because
    # it is intended to remove all case distinctions in a string"
    # Its the Docs recommended ay to do string comparisons
    try:
        return countries[name]
    except KeyError:
        raise ValueError(
            "Unknown country name. "
            f"Country name must be one of: {','.join(valid_country_names)}"
        )


T = TypeVar("T")
BoundedString = Annotated[str, Field(min_length=2, max_length=50)]
BoundedList = Annotated[list[T], Field(min_length=1, max_length=5)]
Country = Annotated[str, AfterValidator(lambda name: lookup_country(name)[0])]


class AutomobileType(Enum):
    sedan = "Sedan"
    coupe = "Coupe"
    convertible = "Convertible"
    suv = "SUV"
    truck = "Truck"


class Automobile(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_default=True,
        validate_assignment=True,
        alias_generator=to_camel,
    )

    id_: UUID4 | None = Field(alias="id", default_factory=uuid4)
    manufacturer: BoundedString
    series_name: BoundedString
    type_: AutomobileType = Field(alias="type")
    is_electric: bool = False
    manufactured_date: date = Field(
        validation_alias="completionDate", ge=date(1980, 1, 1)
    )
    base_msrp_usd: float = Field(
        validation_alias="msrpUSD", serialization_alias="baseMSRPUSD"
    )
    top_features: BoundedList[BoundedString] | None = None
    vin: BoundedString
    number_of_doors: int = Field(
        default=4,
        validation_alias="doors",
        ge=2,
        le=4,
        multiple_of=2,
    )
    registration_country: Country | None = None
    registration_date: date | None = None
    license_plate: BoundedString | None = None

    @field_serializer(
        "manufactured_date", "registration_date", when_used="json-unless-none"
    )
    def serialize_date(self, value: date) -> str:
        return value.strftime("%Y/%m/%d")


api_data = {
    "id": "c4e60f4a-3c7f-4da5-9b3f-07aee50b23e7",
    "manufacturer": "BMW",
    "seriesName": "M4 Competition xDrive",
    "type": "Convertible",
    "isElectric": False,
    "completionDate": "2023-01-01",
    "msrpUSD": 93_300,
    "topFeatures": ["6 cylinders", "all-wheel drive", "convertible"],
    "vin": "1234567890",
    "doors": 2,
    "registrationCountry": "us",
    "registrationDate": "2023-06-01",
    "licensePlate": "AAA-BBB",
}

car = Automobile.model_validate(api_data)

print(car)
pp(car.model_dump_json(), indent=4, compact=False)
