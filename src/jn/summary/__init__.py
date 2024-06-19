from typing import Callable


def wrapped_summarize_notes(cfg) -> Callable[[], None]:
    def inner(arg_list: list[str]) -> None:
        print("'wrapped_summarize_notes' is not yet implemented.")

    return inner


def wrapped_summarize_notes_visual(cfg) -> Callable[[], None]:
    def inner(arg_list: list[str]) -> None:
        print("'wrapped_summarize_notes_visual' is not yet implemented.")

    return inner
