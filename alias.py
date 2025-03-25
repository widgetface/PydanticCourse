"""
Field aliases

use diferent names for serialisation / deserialisation

useful for RESTFUL API's

"""

from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_serializer
from pydantic.alias_generators import to_camel, to_snake, to_pascal
from datetime import date


# Examples


class TestModel(BaseModel):
    id_: int = Field(alias="id", default=7)
    last_name: str = Field(alias="lastName")  # Here camelCase


# OR use
# model_config = ConfigDict(alias_generator=to_camel)
# You don't need to use Field(...)

json_data1 = """
    {
    "id": 1,
    "lastName": "Howie"
    }
    """
test = TestModel.model_validate_json(json_data1)
print(test)  # -> id_=1 last_name='Howie'
print(test.id_)  # To access the field

json_data2 = """
    {
    "lastName": "Howie"
    }
    """
test2 = TestModel.model_validate_json(json_data2)
print(f"test2 = {test2}")

# Alias Generator
# from pydantic.alias_generators import to_camel, to_snake, to_pascal

print(to_camel("first_name"))  # firstName
print(to_pascal("first_name"))  # FirstName
print(to_snake("firstName"))  # first_name


# Using custom functions for aliases is common
# Avoid naming classes ith keywords, mapping between python and JSON.
def make_upper(str: str) -> str:
    return str.upper()


def make_alias(instr: str) -> str:
    alias = to_camel(instr)
    return alias.removesuffix("_")


class TestModel2(BaseModel):
    model_config = ConfigDict(alias_generator=make_upper)
    id_: int
    last_name: str | None = None


print(TestModel2.model_fields)
# Note alias = ID
test2 = TestModel2(ID_=12, LAST_NAME="fred")
print(test2)
# {'id_': FieldInfo(annotation=int, required=True, alias='ID_', alias_priority=1), 'last_name': FieldInfo(annotation=Union[str, NoneType], required=False,
# default=None, alias='LAST_NAME', alias_priority=1)}
print(test2.model_dump(by_alias=True))  # {'ID_': 12, 'LAST_NAME': None}


#  Serialization - set attribute names when model_dump


# Note you CANNOT  use a function to generate a serialization_alias
class TestModel3(BaseModel):
    id_: int = Field(alias="ID", serialization_alias="id")
    first_name: str = Field(alias="firstName", serialization_alias="firstName")


# A bad API rsponse from a third party API
response_data = """ {  
    "ID": 100,
    "firstName": "Joe"
}
"""
m = TestModel3.model_validate_json(response_data)
print(m.model_dump(by_alias=True))  # by_alias = True (use serialization alias)


# Validation alias
class TestModel4(BaseModel):
    first_name: str = Field(validation_alias="firstName")


m = TestModel4(firstName="first_name")

"""
    Why three alias (validation, serialization, alias)

    you can specify a NUMBER of vaidation alias

    from pydantic import AliasChoices

    class MyClass(BaseModel):
        model_config = ConfigDict(alias_generator=to_camel)
        first_name: str = Field(
            validation-alias=AliasChoices("FirstName", "GivenName")
            serialization_alias="GivenName"
        )
    if you have both FirstName and GivenName it takes the last one - YOU DON'T GET WARNING 
    OR ERROR

    Example where this might be useful

    data = {
    "databbases": {
        "redis":{
            "name": ""
            "redis_conn_str": ""
            }
        "postgres":{
            "name": ""
            "pg_conn_str": ""
            }
        }
    }

   class DB(BaseModel):
    name: str
    conn_str: str = Field(validation_alias(AliasChoices("redis_conn_str", "pg_conn_str")))

    dbs = {}
    for k, v in data["databases"].items():
        d = DB.model_validate(v)
        dbs[k] = d

"""

# Project
# From an API


resp_json = """
{
    "manufacturer": "BMW",
    "seriesName": "M4",
    "type": "Convertible",
    "isElectric": false,
    "completionDate": "2023-01-01",
    "msrpUSD": 93300,
    "vin": "1234567890",
    "doors": 2,
    "registrationCountry": "France",
    "licensePlate": "AAA-BBB"
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
