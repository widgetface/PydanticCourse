from uuid import uuid4
from enum import Enum
from typing import Annotated, get_args, TypeVar
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_serializer,
    UUID4,
)
from pydantic.alias_generators import to_camel
from datetime import date
# Annotated just adds metadata to the type hint
# Pydantic makes extensive use of Annotated

# Create an int ith metadata ("metadata". [1,2,3]) you can add as much as you need to
SpecialInt = Annotated[int, "metadata", [1, 2, 3]]

# Access metadata args -> <class 'int'>, 'metadata', [1, 2, 3]
print(get_args(SpecialInt))
# Third party libs like pydantic access the args using get_args


class Model(BaseModel):
    x: int = Field(gt=0, le=100)
    y: int = Field(gt=0, le=100)


# Define annotation to simplify the above repeted code.
# We pass a Field to it as metadata (which pydantic understands)
BoundedInt = Annotated[int, Field(gt=0, le=100)]


class AnnotatedModel(BaseModel):
    x: BoundedInt = 1
    y: BoundedInt = 1


v = AnnotatedModel(x=2, y=99)

print(v)

# Type Variables
T = TypeVar("T")
# This avoids list[Any] - T can be anything
BoundedList = Annotated[list[T], Field(min_length=1, max_length=5)]


class BoundedListExample(BaseModel):
    lizt: BoundedList = [1]  # default = [1]


lz = BoundedListExample(lizt=[1, 2, 3, 4, 5])
print(lz)

# String constraints

StandardString = Annotated[
    str, StringConstraints(to_lower=True, min_length=1, strip_whitespace=True)
]


class StrinConstraintExample(BaseModel):
    word: StandardString


s = StrinConstraintExample(word="  AbCDEfghiJK")
print(s)  # -> word='abcdefghijk'

# PROJECT

BoundedString = Annotated[str, Field(min_length=2, max_length=50)]


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
    manufacturer: BoundedString
    series_name: BoundedString
    type_: AutomobleType = Field(alias="type")
    is_electric: bool = False
    # manufactured_date not bfore 01/01/1980
    manufactured_date: date = Field(validation_alias="completionDate", ge=(1980, 1, 1))
    basic_msrp_usd: float = Field(
        validation_alias="msrpUSD", serialization_alias="baseMSRPUSD"
    )
    top_features: BoundedList = Field(alias="topFeatures")
    vin: BoundedString
    number_of_doors: int = Field(
        default=4, alias="doors", validation_alias="doors", min=2, max=4, multiple_of=2
    )
    reg_country: BoundedString | None = Field(
        default=None,
        alias="registrationCountry",
    )
    license_plate: BoundedString | None = Field(default=None, alias="licensePlate")

    # This is used to change format of manufactured_date
    # when_used="json-unless-none" apply only to json
    @field_serializer("manufactured_date", when_used="json-unless-none")
    def serialize_date(self, value: date) -> str:
        return value.strftime("%Y/%m/%d")
