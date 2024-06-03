#!/usr/bin/env python

import sys
from typing import Any, Callable
import json
import re


NOTES_PATH = "/home/isaac/repos/notes/notes.json"
SUBSET_PATH = "/home/isaac/repos/notes/selected.json"
DEFAULT_NOTE = {"id": None, "text": [], "status": "", "rating": "", "tags": [], "priority": 0.5}
VALID_ADDITIONAL_KEYS = {"id", "tags", "status", "priority", "rating"}








def open_notes():
    with open(NOTES_PATH) as f:
        return json.load(f)


def save_notes(notes: dict) -> None:
    print(notes)
    with open(NOTES_PATH, "w") as f:
        json.dump(notes, f, indent=4)


def pretty_print_note(d: dict) -> str:
    return "\n".join([
        f"\n=============== {d['id']:^4} ===============",
        *d["text"],
        f"    tags: {' | '.join(d['tags'])}",
        f"    status: {d['status']}",
        "------------------------------------"
    ])

def validate_and_convert_value(key: str, value: str) -> Any:
    if value is None:
        return None
    match key:
        case "id":
            return value if value is None else int(value)
        case "tags":
            return value.split(",")
        case "priority":
            priority = None if value.lower() in {"none", "null", ""} else float(priority)
            assert (priority is None) or (0.0 <= priority <= 1.0)
            return priority
        case "status":
            assert value in {"unread", "todo", "hoarded"}, f"Invalid status: {value}"
            return value
        case "rating":
            rating = int(value)
            assert rating in range(1, 6)
            return rating
        case _:
            raise ValueError(f"Invalid key: {key}")


def validate_and_convert_condition(key_condition: str) -> Callable:
    if key_condition is None:
        return None
    key, condition = key_condition.split(":", 1)
    match key:
        case "tags":
            tags = condition.split(",")
            print(tags)
            return lambda d: all([s in d[key] for s in tags])
        case "id":
            expr = f"lambda d: d['{key}'] {condition} if d['{key}'] is not None else False"
            print(expr)
            return eval(expr)
        case "priority":
            f"lambda d: d['{key}'] {condition} if d['{key}'] is not None else False"
            print(expr)
            return eval(expr)
        case "status":
            return lambda d: d[key] == condition if d[key] is not None else False
        case "rating":
            expr = f"lambda d: d['{key}'] {condition} if d['{key}'] is not None else False"
            print(expr)
            return eval(expr)
        case _:
            raise ValueError(f"Invalid key: {key}")


def split_by_predicate(notes: list[dict], predicate: Callable[[dict], bool]) -> tuple[list[dict], list[dict]]:
    yes, no = [], []
    for d in notes:
        (yes if predicate(d) else no).append(d)
    return (yes, no)


def parse_query(args: list[str]) -> Callable:
    if not args:
        print("No query given.")
        sys.exit()
    if args[0].startswith("lambda"):
        return eval(args[0])
    print(".")
    conditions = tuple(map(validate_and_convert_condition, args))
    return lambda d: all(map(lambda f: f(d), conditions))
    

def split_notes(args: list[str]) -> None:
    notes = open_notes()
    condition = parse_query(args)
    subset, notes = split_by_predicate(notes, condition)
    with open(SUBSET_PATH, "w") as f:
        json.dump(subset, f, indent=4)
    save_notes(notes)


def join_notes() -> None:
    ...



def add_note(args: list[str]) -> None:
    if not args:
        return None
    notes = open_notes()
    print(f"{notes=}")
    new_note = DEFAULT_NOTE | {"text": re.split("\\\\n|\n|\\n", args[0])}
    print(f"{new_note=}")
    print(new_note)
    for arg in args[1:]:
        print(f"{arg=}")
        key, value = arg.split(":", 1)
        print(f"{key=}")
        print(f"{value=}")
        value = validate_and_convert_value(key, value)
        print(value)
        new_note.update({key: value})
    if new_note["id"] is None:
        new_note.update({"id": max(map(lambda d: d["id"] or 0, notes)) + 1 if notes else 0})
    notes.append(new_note)
    save_notes(notes)


def commit_and_push(): ...
def add_file(): ...
def import_file(): ...
def export_file(): ...
def split_file(): ...
def join_file(): ...
def show(): ...
def summarize(): ...
def summarize_visual(): ...
def tui(): ...
def sort(): ...

def fetch():
    # need to import matrix-commander to reverse-engineer 'matrix-commander -r '!KeeTeSkGHgkKZTrbpT:matrix.org' --listen-self --listen tail  --tail 15'
    ...

if __name__ == "__main__":
    clargs = sys.argv[1:]

    
    match len(clargs):
        case 0:
            command = "tui"
        case 1: 
            if (first := clargs[0]).startswith("file:") or first.endswith(".json"):
                file_name = first.split(":")[-1]
                command = "tui"
            else:
                command = clargs[0]
        case _:
            if (first := clargs[0]).startswith("file:") or first.endswith(".json"):
                file_name = first.split(":")[-1]
                command = clargs[1]
                args = clargs[2:]
            else:
                command = first
                args = clargs[1:]
            
    print(command)

    function: Callable[[str, str, list[str]], None] = {
        "commit": commit_and_push,
        "add-file": add_file,
        "add": add_note,
        "import": import_file,
        "export": export_file,
        "split": split_file,
        "join": join_file,
        "show": show,
        "summarize": summarize,
        "summarize-visual": summarize_visual,
        "fetch": fetch,
        "tui": tui,
        "sort": sort,
    }[command]

    function(args)

#TODO: refactor argument parsing to a separate function, to be a bit more elegant and robust, as well as more testable
