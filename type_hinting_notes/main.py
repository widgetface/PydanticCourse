"""
uv add mypy
mypy . --pretty
"""

from typing import List, Dict, Set, Optional, Sequence, Literal, TypeVar, Callable

a: str = "Hello"  # 5

color: Literal["Red", "Green"] = "Green"


# Here e have to set int = None
def my_func(x: Optional[int] = None) -> int:
    return 2 * x if x else 2


# Here a Sequence could be a list , tuple
# For a sepecific type in Sequence = Sequence[str] # ("a", "b")
def my_func2(seq: Sequence) -> Sequence:
    return seq


print(my_func())

# # Generics https://medium.com/@steveYeah/using-generics-in-python-99010e5056eb
# If you are using type hints in Python and static analysis tools such
# as mypy, then you have probably used the Any type quite often to
# get around typing functions and methods where the type of an
# argument can vary at runtime. While Any itself is a very convenient
# tool that enables gradual typing in Python code (the ability to add
# type hints to your code little by little over time), it doesn’t add any real value in terms of portraying
# knowledge to the reader. This is where generics come in.

T = TypeVar("T")


def first(container: List[T]) -> T:
    return container[0]


if __name__ == "__main__":
    list_one: List[str] = ["a", "b", "c"]
    print(first(list_one))

    list_two: List[int] = [1, 2, 3]
    print(first(list_two))

K = TypeVar("K")
V = TypeVar("V")


def get_item(key: K, container: Dict[K, V]) -> V | None:
    return container.get(key, None)


if __name__ == "__main__":
    test: Dict[str, int] = {"k": 1}
    print(get_item("a", test))  # None
    print(get_item("k", test))  # 1

# listing the types that are allowed
# T = TypeVar("T", str, int)  # T can only represent types of int and str
# U = TypeVar("T", bound=int)  # U can only be an int or subtype of int


# using generics in a class
# extending the Generic base class
# define T which is then used within methods of the Registry class.


def fun(x: int) -> int:
    return x * x


# You have to specify the correct signature for the Callable: Callable[[int], int]
def takes_fun(f: Callable[[int], int]) -> int:
    return f(2)


takes_fun(fun)


# lambda
# a: Callable[[int], int] = lambda x : x + 10
