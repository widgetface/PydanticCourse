import typing as t
import collections.abc as c

# typing is deprecated after Python 3.9


def say_hello(names: t.Sequence[str]) -> str:
    return f"Heelo{names[0]}"


# Now Python 3.10
# No use collections.abc


def say_hello_no(names: c.Sequence[str]) -> str:
    return f"Heelo{names[0]}"


# Sized is a special abstract base class (ABC) from the collections.abc module
# that is used to define objects that have a size
def get_size(s: c.Sized) -> int:
    return len(s)  # This will call the __len__() method of the object


# BUT


def example(x: t.Literal["red", "green"]) -> str:
    return f"color is {x}"
