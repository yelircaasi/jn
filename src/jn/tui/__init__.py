from typing import Callable


def wrapped_tui_loop(cfg) -> Callable[[], None]:
    def inner(arg_list: list[str]) -> None:
        print("'wrapped_tui_loop' is not yet implemented.")

    return inner
