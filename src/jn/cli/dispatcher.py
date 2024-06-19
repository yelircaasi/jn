from typing import Callable

# from .arg_parser import parse_args

from ..configuration import initialize_config
from ..editing import wrapped_add_note, wrapped_edit_subset, wrapped_extract_subset, wrapped_return_subset
from ..display import wrapped_show_subset
from ..summary import wrapped_summarize_notes, wrapped_summarize_notes_visual
from ..sync import wrapped_commit_and_push, wrapped_fetch_from_everywhere
from ..tui import wrapped_tui_loop
from ..validation import wrapped_validate_notes


def wrapped_help(cfg) -> Callable[[], None]:
    def inner(arg_list: list[str]) -> None:
        print("'wrapped_help' is not yet implemented.")

    return inner

def dispatch_from_arguments(args: list[str]) -> Callable:

    config = 42 #initialize_config()

    # command, positional, attributes, options = parse_args(args)
    command = args[0] if args else "help"
    args = tuple(args[1:])

    function: Callable[[list[str]], None] = {
        "commit": wrapped_commit_and_push,
        "add": wrapped_add_note,
        "edit": wrapped_edit_subset,
        "extract": wrapped_extract_subset,
        "help": wrapped_help,
        "return": wrapped_return_subset,
        "show": wrapped_show_subset,
        "summarize": wrapped_summarize_notes,
        "summarize-visual": wrapped_summarize_notes_visual,
        "fetch": wrapped_fetch_from_everywhere,
        "tui": wrapped_tui_loop,
        "validate": wrapped_validate_notes
    }[command](config)

    print(type(function))

    # function(positional, attributes, options)
    function(args)
