"""
Course on Pydantic V2

"""

from pprint import pp  # Use pretty print
from pydantic import BaseModel, ValidationError


class Person(BaseModel):
    first_name: str
    last_name: str
    age: int

    @property
    def full_name(self):
        print(f"{self.first_name} {self.last_name}")


# Create Person instance different ways
data = {"first_name": "Joe", "last_name": "Doe", "age": 60}
dad: Person = Person(first_name="John", last_name="Doe", age=22)
son = Person.model_validate(data)
son2: Person = Person(**data)
data_json = """
{
    "first_name": "Isaac",
    "last_name": "Newton",
    "age": 84
}
"""
son3 = Person.model_validate_json(data_json)
# Instances of Person
pp(dad)
print(dad.full_name)
# Info about fields
pp(dad.model_fields)

# ValidationError Example
try:
    p = Person(first_name="Dan", last_name="Doe")
except ValidationError as e:
    pp(e)
finally:
    print("ValidationError error example")

# serialize

print(dad.model_dump())  #
print(dad.model_dump(exclude="age"))
print(dad.model_dump(include="age"))
print(dad.model_dump_json(indent=4))
print(dad.model_fields_set)  # which fileds were set (not default)


# Type coercion


class Coordinates(BaseModel):
    x: float
    y: float


p1 = Coordinates(x=1.3, y=-55.8)
p2 = Coordinates(x=1.3, y="-90.8")  # Here the coercion works fine
print(f"Coordinate example {p1} and {p2}")

# Optional / Nullable


class Circle(BaseModel):
    center: tuple[int, int] = (0, 0)  # makes the field Optional
    radius: int
    nullable: int | None  # This is how to set a nullable field (NOT Optional)
    nullable_default: str | None = None  # nullable and default(None)


# REMEMBER DEFAULT VALUES AREN'T VALIDATED
# center: tuple(int, int) = "junk"  IS OK
# Can turn ob default validation

# Center(radius=1, nullable=None)

# JSON schema generation


class Example(BaseModel):
    field1: int | None = None
    field2: str = "Python"


# to see schema (simple method)
pp(Example.model_json_schema())

# Pydantic allows automatic creation and customization of JSON
#  schemas from models. The generated JSON schemas are
# compliant with the following specifications:

# JSON Schema Draft 2020-12
# OpenAPI Specification v3.1.0.

# See https://docs.pydantic.dev/latest/concepts/json_schema/#generating-json-schema
