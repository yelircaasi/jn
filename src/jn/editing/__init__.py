from typing import Callable

from ..query import parse_query


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
        print("'wrapped_extract_subset' is not yet fully implemented.\n")
        query = "".join(arg_list)
        parse_query(query)

    return inner


def wrapped_test_query(cfg) -> Callable[[], None]:
    def inner(arg_list: list[str]) -> None:
        print("'wrapped_test_query' is not yet fully implemented.\n")
        print(arg_list)
        query = "".join(arg_list)
        parsed = parse_query(query)

    return inner


def wrapped_return_subset(cfg) -> Callable[[], None]:
    def inner(arg_list: list[str]) -> None:
        print("'wrapped_return_subset' is not yet implemented.")

    return inner
