from uuid import uuid4
from pprint import pp
from math import pi
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
    PlainSerializer,
    UUID4,
    ValidationInfo,
)
from pydantic.alias_generators import to_camel
from datetime import date, datetime
from dateutil.parser import parse

# Attach properties to pydantic model


class PropModel(BaseModel):
    center: tuple[int, int] = (0, 0)
    radius: int = Field(default=1, gt=0)

    # Use a method to get area example
    def area(self):
        return pi * self.radius**2

    @property
    def cicumference(self):
        return (2 * pi) * self.radius


circle = PropModel(center=(3, 4), radius=5)
print(circle.area())
print(circle.cicumference)


# You can attach a serializer to an annotated type
#
# Serialize datetime strings of different formts e.g. ("2020/1/1 6pm")
# always store the datetime as UTC aware ()
# See PydanticCourse/utc_information.txt
# serialize the dataetime to a  datatime object  hen serializing to a Python dict
# serializes to JSON using the following format YYY/MM/DD HH:MM: AM/PM (UTC)


def make_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    else:
        dt = dt.astimezone(pytz.utc)
    return dt


def parse_datetime(value: str):
    if isinstance(value, str):
        try:
            return parse(value)
        except Exception as ex:
            raise ValueError(str(ex))
    return value


def dt_json_serializer(dt: datetime) -> str:
    return dt.strftime("%Y/%m/%d %I:%M %p UTC")


# Added PlainSerializer
# This approach alows us to reuse the validators / formatters
# across projects or classes
DateTimeUTC = Annotated[
    datetime,
    BeforeValidator(parse_datetime),  # Format to validable string
    AfterValidator(make_utc),  # Format to UTC
    # Now a step to ensure
    # Serializes to JSON using the following format YYY/MM/DD HH:MM: AM/PM (UTC)
    PlainSerializer(dt_json_serializer, when_used="json-unless-none"),
]


class Example(BaseModel):
    dt: DateTimeUTC


m = Example(dt="2024/1/1 3pm")
pp(m.model_dump_json())  # '{"dt":"2024/01/01 03:00 PM UTC"}'


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


def serialize_date(value: date) -> str:
    return value.strftime("%Y/%m/%d")


T = TypeVar("T")
BoundedString = Annotated[str, Field(min_length=2, max_length=50)]
BoundedList = Annotated[list[T], Field(min_length=1, max_length=5)]
Country = Annotated[str, AfterValidator(lambda name: lookup_country(name)[0])]
CustomDate = Annotated[
    datetime, PlainSerializer(serialize_date, when_used="json-unless-none")
]


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
    manufactured_date: CustomDate = Field(
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
    registration_date: CustomDate | None = None
    license_plate: BoundedString | None = None

    # Moved to annotated type
    # @field_serializer(
    #     "manufactured_date", "registration_date", when_used="json-unless-none"
    # )
    # def serialize_date(self, value: date) -> str:
    #     return value.strftime("%Y/%m/%d")


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
