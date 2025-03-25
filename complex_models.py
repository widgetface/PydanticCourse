from uuid import uuid4
from pprint import pp
from math import pi
import pytz
from enum import Enum
from functools import cached_property
from typing import Annotated, get_args, TypeVar
from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    computed_field,
    ConfigDict,
    EmailStr,
    Field,
    FieldSerializationInfo,
    StringConstraints,
    field_serializer,
    field_validator,
    PlainSerializer,
    PastDate,
    UUID4,
    ValidationInfo,
)
from pydantic.alias_generators import to_camel, to_pascal
from datetime import date, datetime
from dateutil.parser import parse

# Use Pydntic mdeols to descibe attributes in another Pydantic model


class Point(BaseModel):
    x: int
    y: int


class Circle(BaseModel):
    center: Point
    radius: int = Field(default=1, gt=0)


p = Point(x=6, y=8)
# print(p.model_dump())
m = Circle(center=p, radius=10)
# print(m.model_dump())
m2 = Circle(center={"x": 3, "y": 6}, radius=8)
# print(m2.model_dump())
# print(m2.center.x)

# One of the useful things about model composition, is that each model used can be independently configured.
# For example, suppose we have this piece of JSON we are receiving from some API call.
# We are interested in only a SUBSET of the information, so we can easily create models that can ignore these extra pieces of data.

json_data = """
{
    "firstName": "David",
    "lastName": "Hilbert",
    "contactInfo": {
        "email": "d.hilbert@spectral-theory.com",
        "homePhone": {
           "countryCode": 49,
            "areaCode": 551,
            "localPhoneNumber": 123456789
        }
    },
    "personalInfo": {
        "nationality": "German",
        "born": {
            "date": "1862-01-23",
            "place": {
                "city": "Konigsberg",
                "country": "Prussia"
            }
        },
        "died": {
            "date": "1943-02-14",
            "place": {
                "city": "Gottingen",
                "country": "Germany"
            }
        }
    },
    "awards": ["Lobachevsky Prize", "Bolyai Prize", "ForMemRS"],
    "notableStudents": ["von Neumann", "Weyl", "Courant", "Zermelo"]
}
"""
# So use annotated types to get
# contactInfo.email
# born.place and born.date


class ContactInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    email: EmailStr | None = None


class PlaceInfo(BaseModel):
    city: str
    country: str


class PlaceDateInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    date_: PastDate = Field(alias="date")
    place: PlaceInfo


class PersonalInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    nationality: str
    born: PlaceDateInfo


SortedStringList = Annotated[
    list[str], AfterValidator(lambda x: sorted(x, key=str.casefold))
]


class Person(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )

    first_name: str
    last_name: str
    contact_info: ContactInfo
    personal_info: PersonalInfo
    notable_students: SortedStringList = Field(default=[], repr=False)


# JUST GET THE REQUIRED FIELDS FROM JSON
person = Person.model_validate_json(json_data=json_data)
pp(person.model_dump_json(indent=2))


# Model Inheritence
# Create  custom base model and it just has a configuration


class CustomModel(BaseModel):
    model_config = ConfigDict(
        extra="ignore", alias_generator=to_camel, populate_by_name=True
    )


class PersonInheritence(CustomModel):
    model_config = ConfigDict(strict=False)  # override parent
    first_name: str
    last_name: str
    contact_info: ContactInfo
    personal_info: PersonalInfo
    notable_students: SortedStringList = Field(default=[], repr=False)


person2 = PersonInheritence.model_validate_json(json_data=json_data)
pp(person2.model_dump_json(indent=2))

## Composition and Inheritence
# Another use for inheritance might be because you want all your models
#  to contain certain fields.

# For example, you might be creating a REST API, and you want every response
# from your API to include some basic information about the request:
# maybe a unique ID, the date
# and time the request was made, and how long it took to execute.

json_data = """
{
    "firstName": "David",
    "lastName": "Hilbert",
    "contactInfo": {
        "email": "d.hilbert@spectral-theory.com",
        "homePhone": {
            "countryCode": 49,
            "areaCode": 551,
            "localPhoneNumber": 123456789
        }
    },
    "personalInfo": {
        "nationality": "German",
        "born": {
            "date": "1862-01-23",
            "place": {
                "city": "Konigsberg",
                "country": "Prussia"
            }
        },
        "died": {
            "date": "1943-02-14",
            "place": {
                "city": "Gottingen",
                "country": "Germany"
            }
        }
    },
    "awards": ["Lobachevsky Prize", "Bolyai Prize", "ForMemRS"],
    "notableStudents": ["von Neumann", "Weyl", "Courant", "Zermelo"]
}
"""


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


def dt_serializer(dt, info: FieldSerializationInfo) -> datetime | str:
    if info.mode_is_json():
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return dt


DateTimeUTC = Annotated[
    datetime,
    BeforeValidator(parse_datetime),
    AfterValidator(make_utc),
    PlainSerializer(dt_serializer, when_used="unless-none"),
]


class CustomBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="ignore", alias_generator=to_camel, populate_by_name=True
    )


class RequestInfo(CustomBaseModel):
    query_id: uuid4 = Field(default_factory=uuid4)
    execution_dt: DateTimeUTC = Field(default_factory=lambda: datetime.now(pytz.utc))
    elapsed_time_secs: float


class ResponseBaseModel(CustomBaseModel):
    request_info: RequestInfo


# And now, we can use this ResponseBaseModel as the base for all our response models in our API.
class Users(ResponseBaseModel):
    users: list[str] = []


users = Users(
    request_info=RequestInfo(elapsed_time_secs=3.14),
    users=["Athos", "Porthos", "Aramis"],
)
print(users.model_dump_json(by_alias=True, indent=2))

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


country_code_lookup = {name: code for name, code in countries.values()}


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


class CamelBasedModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_default=True,
        validate_assignment=True,
        alias_generator=to_camel,
    )


class RegistrationCountry(CamelBasedModel):
    name: Country | None = None

    @computed_field
    @cached_property
    def code3(self) -> str:
        return country_code_lookup[self.name]


class Automobile(CamelBasedModel):
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
    registration_country: RegistrationCountry | None
    registration_date: CustomDate | None = None
    license_plate: BoundedString | None = None


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
    "registrationCountry": {"name": "us"},
    "registrationDate": "2023-06-01",
    "licensePlate": "AAA-BBB",
}

car = Automobile.model_validate(api_data)

print(car)
pp(car.model_dump_json(), indent=4, compact=False)
