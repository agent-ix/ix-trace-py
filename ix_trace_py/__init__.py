import re
from collections.abc import Callable
from typing import TypeVar


def hello():
    return "Hello, World!"


_T = TypeVar("_T")

_ID_SHAPE = re.compile(r"[A-Za-z][A-Za-z0-9_]*(?:-[A-Za-z0-9]+)+")
_DIGIT = re.compile(r"[0-9]")


def _is_id_shaped(value: str) -> bool:
    """Shape only, never membership: KIND, then hyphenated alphanumeric segments."""
    if _ID_SHAPE.fullmatch(value) is None:
        return False
    return any(_DIGIT.search(segment) for segment in value.split("-")[1:])


def implements(*ids: str) -> Callable[[_T], _T]:
    """Declare the specification ids a production symbol implements.

    Returns an identity decorator: the decorated function or class is returned
    unchanged. The ids are checked once, when the decorator expression runs.
    """
    if not ids:
        raise ValueError(
            'implements() needs at least one id, e.g. implements("FR-007-AC-1")'
        )
    for position, value in enumerate(ids):
        if not isinstance(value, str):
            raise TypeError(
                f"implements() argument {position} must be a str, "
                f"got {type(value).__name__}"
            )
        if not _is_id_shaped(value):
            raise ValueError(
                f"implements() argument {position} is not an id-shaped "
                f"string: {value!r}"
            )

    def decorator(target: _T) -> _T:
        return target

    return decorator
