from typing import Callable

from . import parse_args


def dispatch_from_arguments(args: list[str]) -> Callable:

    command, positional, attributes, options = parse_args(args)

    function: Callable[[str, str, list[str]], None] = {
        # "commit": commit_and_push,
        # "add-file": add_file,
        # "add": add_note,
        # "import": import_file,
        # "export": export_file,
        # "split": split_file,
        # "join": join_file,
        # "show": show,
        # "summarize": summarize,
        # "summarize-visual": summarize_visual,
        # "fetch": fetch,
        # "tui": tui,
        # "sort": sort,
    }[command]

    function(positional, attributes, options)
