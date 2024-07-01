"""
Still just scratch at this point.
"""

import re
from typing import Any, Callable


def parse_id(subquery: str) -> Callable[[dict[str, Any]], bool]:
    assert re.match("=[A-Za-z,]+|=\[[A-Za-z]\]+", subquery)

    if subquery.startswith("=["):
        rgx = re.compile(subquery[2:-1])
        return lambda d: re.search(rgx, d["id"])
    # elif subquery.startswith("="):
    else:
        sq = subquery[1:]
        return lambda d: sq == d["id"]


def parse_tags(subquery: str) -> Callable[[dict[str, Any]], bool]:
    assert re.match("^\?[A-Za-z\[\]\.,]", subquery)
    subquery += ":"
    tag_query, subtag_query = re.split(":+", subquery)[1:3]
    tag_match_empty = bool(re.match("^::", subquery))
    subtag_match_empty = bool(re.match("^:+[A-Za-z]+::"))

    tag_condition = parse_tag_dsl(tag_query, include_empty=tag_match_empty)
    subtag_condition = parse_tag_dsl(subtag_query, include_empty=subtag_match_empty)

    return lambda d: tag_condition(d) and subtag_condition(d)


def parse_type(subquery: str) -> Callable[[dict[str, Any]], bool]:
    assert re.match("^:", subquery)

    if subquery.startswith(""):
        _test = ...
    else:
        _test = ...
    return _test


def parse_status(subquery: str) -> Callable[[dict[str, Any]], bool]:
    assert re.match("^~", subquery)

    if subquery.startswith(""):
        _test = ...
    else:
        _test = ...
    return _test


def parse_due_date(subquery: str) -> Callable[[dict[str, Any]], bool]:
    assert re.match("^\^~?{1,2}\d{4}-\d\d-\d\d", subquery)

    if subquery.startswith("^^"):
        _test = ...
    else:
        _test = ...
    return _test


def parse_rating(subquery: str) -> Callable[[dict[str, Any]], bool]:
    m = re.match("^\*+~?$", subquery)
    assert m
    sq = m.group(0)

    if subquery.endswith("?~") or subquery.endswith("?~"):
        return lambda d: d["rating"] in sq
    elif subquery.endswith("opt"):
        return lambda d: (d["rating"]) or not (bool(d["rating"]))
    elif subquery.endswith("~"):
        return lambda d: d["rating"] in sq
    else:
        return lambda d: sq in d["rating"]


def parse_date(subquery: str) -> Callable[[dict[str, Any]], bool]:
    m = re.match("^\^{1,2}~?(\d{4}-\d\d-\d\d)$", subquery)
    assert bool(m)
    date = m.group(1)

    if subquery.startswith("^^~"):
        return lambda d: d[""]
    elif subquery.startswith("^^"):
        return ...
    elif subquery.startswith("^~"):
        return ...
    elif subquery.startswith("^"):
        return ...


def parse_extra_attribute(subquery: str) -> Callable[[dict[str, Any]], bool]:
    assert re.match("^\+", subquery)

    if subquery.startswith("++"):
        _test = ...
    else:
        _test = ...
    return _test


def parse_language(subquery: str) -> Callable[[dict[str, Any]], bool]:
    assert re.match("^_", subquery)

    if subquery.startswith("__"):
        _test = ...
    else:
        _test = ...
    return _test


dispatcher = {
    "=": parse_id,
    "?": parse_tags,
    ":": parse_type,
    "%": parse_status,
    "*": parse_rating,
    "^": parse_date,
    "+": parse_extra_attribute,
    "_": parse_language,
}

order = {
    "=": 0,
    "?": 1,
    ":": 2,
    "~": 3,
    "%": 4,
    "*": 5,
    "^": 6,
    "+": 7,
    "_": 8,
}


def make_item_parser(config: ...) -> Callable[[str], Callable[[dict], bool]]:
    def parse_item(item: str) -> Callable[[dict], bool]: ...

    return parse_item
