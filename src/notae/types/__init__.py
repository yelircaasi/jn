from typing import Literal, TypedDict

__all__ = ["NoteType"]


note_types = {}
TypeType = Literal["book", "idea", "link", "docLink", ""]

class NoteDict(TypedDict):
    id: int
    type: TypeType
    tags: list[str]
    status: list[str]
