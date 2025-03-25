from enum import Enum
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_serializer,
    PositiveInt,
    PastDate,
    conlist,
    UUID4,
)
from pydantic.alias_generators import to_camel, to_snake, to_pascal
from datetime import date


"""

# To date
# resp_json = """
{
    "manufacturer": "BMW",
    "seriesName": "M4",
    "type": "Convertible",
    "isElectric": "false",
    "completionDate": "2023-01-01",
    "msrpUSD": 93300,
    "vin": "1234567890",
    "doors": 2,
    "registrationCountry": "France",
    "licensePlate": "AAA-BBB",
}
"""

# When serialized '
# expected_serialized_dict = {
#     'manufacturer': 'BMW',
#     'series_name': 'M4',
#     'type_': AutomobileType.convertible,
#     'is_electric': False,
#     'manufactured_date': date(2023, 1, 1),
#     'base_msrp_usd': 93300.0,
#     'vin': '1234567890',
#     'number_of_doors': 2,
#     'registration_country': 'France',
#     'license_plate': 'AAA-BBB'
# }

# expected_serialized_json_by_alias = (
#     '{"manufacturer":"BMW","seriesName":"M4","type":"Convertible",'
#     '"isElectric":false,"manufacturedDate":"2023/01/01","baseMSRPUSD":93300.0,'
#     '"vin":"1234567890","numberOfDoors":2,"registrationCountry":"France",'
#     '"licensePlate":"AAA-BBB"}'
# )


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
    manufacturer: str
    series_name: str
    type_: AutomobleType = Field(alias="type")
    is_electric: bool = False
    manufactured_date: date = Field(validation_alias="completionDate")
    basic_msrp_usd: float = Field(
        validation_alias="msrpUSD", serialization_alias="baseMSRPUSD"
    )
    vin: str
    number_of_doors: int = Field(default=4, alias="doors", validation_alias="doors")
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


car = Automobile.model_validate_json(resp_json)
print(car)

"""

# Pydantic provides many specialised types
# See https://docs.pydantic.dev/latest/api/types/

# e.g
# PositiveInt (only positive ints)
# conlist (min , ma list size)
# PastDate - datetime must be in past
# HttpUrl -validate valid https url (and parse the url)
# EmailStr - validate email address
# UUID import uuid and from pydantic import UUID1, BaseModel

# PositiveInt (only positive ints)
# Equivilent ty[pe hinting PositiveInt = Annotated[int, Gt(0)]


class ExampleTypes(BaseModel):
    positive_int: PositiveInt = Field(default=1)  # Has to be > 0
    con_list: list = conlist(
        type=int, min_length=1, max_length=3
    )  # constrained list[int]
    date_: date = PastDate  # Pydantic assumes its localtime
    email: EmailStr


# Model(email=NameEmail(name='john.smith', email='john.smith@some-domain.com'))
# m.email.name -> 'john.smith'

# url = AnyUrl("https://www.google.com/search?q=pydantic")
# print(f"{url.scheme=}")
# print(f"{url.host=}")
# print(f"{url.path=}")
# print(f"{url.query=}")
# print(f"{url.port=}")
# print(f"{url.username=}")
# print(f"{url.password=}")

# Project


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
    id_: UUID4 | None = Field(default=None, alias="id")
    manufacturer: str
    series_name: str
    type_: AutomobleType = Field(alias="type")
    is_electric: bool = False
    manufactured_date: date = Field(validation_alias="completionDate")
    basic_msrp_usd: float = Field(
        validation_alias="msrpUSD", serialization_alias="baseMSRPUSD"
    )
    vin: str
    number_of_doors: int = Field(default=4, alias="doors", validation_alias="doors")
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
