from typing import Callable

from pydantic import TypeAdapter

from ..types import NoteDict


# note_adapter = TypeAdapter(NoteDict)

def wrapped_validate_notes(cfg) -> Callable[[], None]:
    def inner(arg_list: list[str]) -> None:
        print("'wrapped_validate_notes' is not yet implemented.")

    return inner


# __all__ = ["note_adapter", "wrapped_validate"]








