from typing import Callable


def wrapped_show_subset(cfg) -> Callable[[], None]:
    def inner(arg_list: list[str]) -> None:
        print("'wrapped_show_subset' is not yet implemented.")

    return inner