from typing import Callable


def wrapped_commit_and_push(cfg) -> Callable[[], None]:
    def inner(arg_list: list[str]) -> None:
        print("'wrapped_commit_and_push' is not yet implemented.")

    return inner


def wrapped_fetch_from_everywhere(cfg) -> Callable[[], None]:
    def inner(arg_list: list[str]) -> None:
        print("'wrapped_fetch_from_everywhere' is not yet implemented.")

    return inner
