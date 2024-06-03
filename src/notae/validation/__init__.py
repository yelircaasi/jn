
from pydantic import TypeAdapter

from ..types import NoteDict


note_adapter = TypeAdapter(NoteDict)

__all__ = ["note_adapter"]