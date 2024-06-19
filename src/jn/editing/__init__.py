from typing import Callable


def wrapped_add_note(cfg) -> Callable[[], None]:
    def inner(arg_list: list[str]) -> None:
        print("'wrapped_add_note' is not yet implemented.")

    return inner


def wrapped_edit_subset(cfg) -> Callable[[], None]:
    def inner(arg_list: list[str]) -> None:
        print("'wrapped_edit_subset' is not yet implemented.")

    return inner


def wrapped_extract_subset(cfg) -> Callable[[], None]:
    def inner(arg_list: list[str]) -> None:
        print("'wrapped_extract_subset' is not yet implemented.")

    return inner


def wrapped_return_subset(cfg) -> Callable[[], None]:
    def inner(arg_list: list[str]) -> None:
        print("'wrapped_return_subset' is not yet implemented.")

    return inner
