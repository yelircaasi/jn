from typing import Callable


def wrapped_add_note(cfg) -> Callable[[], None]:
    def inner(arg_list: list[str]) -> None:
        print("'wrapped_add_note' is not yet implemented.")

    return inner


def wrapped_edit_subset(cfg) -> Callable[[], None]:
    def inner(arg_list: list[str]) -> None:
        print("'wrapped_edit_subset' is not yet implemented.")

    return inner


def wrapped_export_subset(cfg) -> Callable[[], None]:
    def inner(arg_list: list[str]) -> None:
        print("'wrapped_export_subset' is not yet implemented.")

    return inner
