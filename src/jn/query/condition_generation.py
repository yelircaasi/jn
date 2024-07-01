import re
from typing import Any, Callable
from operator import not_ as negate


identity = lambda x: x


def match_empty(item: Any) -> bool:
    return not bool(item)


def condition_from_tag(subdict: dict, key="tags") -> Callable[[dict], bool]:
    optional = subdict.get("OPTIONAL", False)
    if "NOT" in subdict:
        modify = negate if subdict.get("NOT") else identity
        subdict = subdict["NOT"]
    if "STRING" in subdict:
        tag = subdict["STRING"]
        tag_condition = (
            (lambda d: match_empty(d[key]) or modify(tag in d[key])) if optional else lambda d: modify(tag in d[key])
        )
    elif "REGEX" in subdict:
        reg = re.compile(subdict["REGEX"])
        found = lambda tag: re.search(reg, tag)
        tag_condition = (
            (lambda d: match_empty(d[key]) or modify(any(map(found, d[key]))))
            if optional
            else lambda d: modify(any(map(found, d[key])))
        )
    if "SUBTAG" in subdict:
        subtag_condition = condition_from_tag(subdict["SUBTAG"], key="subtags")
        return lambda d: tag_condition(d) and subtag_condition(d)
    return tag_condition


def condition_from_extra(subdict: dict) -> Callable[[dict], bool]:
    modify = negate if subdict.get("NEGATE") else identity
    optional = subdict.get("OPTIONAL", False)
    return


def condition_from_type(subdict: dict, key="tags") -> Callable[[dict], bool]:
    modify = negate if subdict.get("NEGATE") else identity
    optional = subdict.get("OPTIONAL", False)
    return  # TODO


def condition_from_date_created(subdict: dict) -> Callable[[dict], bool]:
    modify = negate if subdict.get("NEGATE") else identity
    optional = subdict.get("OPTIONAL", False)
    return  # TODO


def condition_from_date_modified(subdict: dict) -> Callable[[dict], bool]:
    modify = negate if subdict.get("NEGATE") else identity
    optional = subdict.get("OPTIONAL", False)
    return  # TODO


def condition_from_type(subdict: dict) -> Callable[[dict], bool]:
    modify = negate if subdict.get("NEGATE") else identity
    optional = subdict.get("OPTIONAL", False)
    return  # TODO


def condition_from_status(subdict: dict) -> Callable[[dict], bool]:
    modify = negate if subdict.get("NEGATE") else identity
    optional = subdict.get("OPTIONAL", False)
    return  # TODO


def condition_from_rating(subdict: dict) -> Callable[[dict], bool]:
    modify = negate if subdict.get("NEGATE") else identity
    optional = subdict.get("OPTIONAL", False)
    return  # TODO


def condition_from_language(subdict: dict) -> Callable[[dict], bool]:
    modify = negate if subdict.get("NEGATE") else identity
    optional = subdict.get("OPTIONAL", False)
    return  # TODO


def condition_from_proglang(subdict: dict) -> Callable[[dict], bool]:
    modify = negate if subdict.get("NEGATE") else identity
    optional = subdict.get("OPTIONAL", False)
    return  # TODO


def condition_from_id(subdict: dict) -> Callable[[dict], bool]:
    modify = negate if subdict.get("NEGATE") else identity
    optional = subdict.get("OPTIONAL", False)
    return  # TODO


dispatcher = {
    "TAG": condition_from_tag,
    "ID": condition_from_id,
    "DATE_CREATED": condition_from_date_created,
    "DATE_MODIFIED": condition_from_date_modified,
    "STATUS": condition_from_status,
    "RATING": condition_from_rating,
    "LANGUAGE": condition_from_language,
    "TYPE": condition_from_type,
    "PROGLANG": condition_from_proglang,
    "EXTRA": condition_from_extra,
}


def make_condition_from_dict(config: ...) -> Callable:

    # condition_from_string = make_item_parser(config)

    def condition_from_dict(query_tree: dict) -> Callable:
        def condition_from_subdict(element: str | dict) -> Callable[[dict], bool]:
            assert len(keys := list(element.keys())) == 1
            key = keys[0]
            return dispatcher[key](element[key])

        if "AND" in query_tree:
            return lambda d: all(map(lambda f: f(d), map(condition_from_subdict, query_tree["AND"])))
        elif "OR" in query_tree:
            return lambda d: any(map(lambda f: f(d), map(condition_from_subdict, query_tree["OR"])))
        else:
            raise ValueError

    return condition_from_dict
