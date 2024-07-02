import re
from typing import Any, Callable

from .item_parser import make_item_parser
from .subparsers import parse_homogeneous
from .lists import IDENT_TYPES, PREFIX_TO_TYPE
from .tokenizer import make_tokenizer
from .subparsers import non_tag_dispatcher


def parse_expression(tokens):

    def parse_primary(tokens):
        def parse_modifiers(tokens):
            ...

        if not tokens:
            return None

        token = tokens.pop(0)
        if (toktype := token[0]) in {"AND", "NOT", "OR"}:
            return (toktype, parse_primary(tokens))

        if (toktype := token[0]) in IDENT_TYPES:
            if toktype == "IDENTIFIER":
                if tokens and tokens[0][0] == "BIND":
                    tokens.pop(0)
                    _, subtag = tokens.pop(0)
                    return (
                        "TAG",
                        ("STRING", token[1]),
                        ("SUBTAG", ("STRING", subtag)),
                    )  # queries of the type tag:{subtag1.subtag2} currenty note supported; instead tag:subtag1.tag:subtag2
                return ("TAG", ("STRING", token[1]))
            if toktype == "REGEX_FULL_OPEN":
                _, rgx = tokens.pop(0)
                tokens.pop(0)
                return ("REGEX_FULL", ("REGEX", rgx))
            if toktype == "REGEX_TEXT_OPEN":
                _, rgx = tokens.pop(0)
                tokens.pop(0)
                return ("REGEX_TEXT", ("REGEX", rgx))
            if toktype == "REGEX_LINK_OPEN":
                _, rgx = tokens.pop(0)
                tokens.pop(0)
                return ("REGEX_LINK", ("REGEX", rgx))
            if toktype == "REGEX_EMBEDDED_OPEN":
                _, rgx = tokens.pop(0)
                tokens.pop(0)
                return ("TAG", ("REGEX", rgx))

        if toktype in non_tag_dispatcher:
            # expr = parse_homogeneous(tokens, PREFIX_TO_TYPE[toktype])
            return non_tag_dispatcher[toktype](tokens)
            # return ("EXPR", expr)
        if token[0] == "LBRACE":
            expr = parse_expression(tokens)
            if tokens and tokens[0][0] == "RBRACE":
                tokens.pop(0)
            return expr

        raise SyntaxError(f"Unexpected token: {token}")

    def parse_and(tokens):
        left = parse_primary(tokens)
        while tokens and tokens[0][0] == "AND":
            tokens.pop(0)
            right = parse_primary(tokens)
            left = ("AND", left, right)
        return left

    def parse_or(tokens):
        left = parse_and(tokens)
        while tokens and tokens[0][0] == "OR":
            tokens.pop(0)
            right = parse_and(tokens)
            left = ("OR", left, right)
        return left

    return parse_or(tokens)


def generate_dict_structure(ast):
    def parse_tag(item: tuple[tuple[str, tuple[str, str]]]) -> dict[str, str]:
        d = {ast[0]: dict(ast[1:])}
        if "SUBTAG" in d["TAG"]:
            d["TAG"]["SUBTAG"] = dict((d["TAG"]["SUBTAG"],))
        return d

    def parse_item(item: tuple[tuple[str, tuple[str, str]]]) -> dict[str, str]:
        def _dict(tuples: list[tuple[str, Any]]) -> dict:
            d = {}
            for t in tuples:
                k, v = t[0], t[1:]
                if (len(v) == 1) and isinstance(v[0], tuple):
                    v = v[0]
                if k in {"SUBTYPE", "SUBTAG", "NOT", "OPT", "EXACT"}:
                    d.update({k: generate_dict_structure(v)})
                else:
                    if len(v) == 1:
                        d.update({k: v[0]})
                    elif len(v) == 2:
                        d.update({k: {v[0]: v[1]}})
                    else: raise ValueError
            return d
        
        if ast[0] in {"NOT", "OPT", "EXACT"}:
            return (ast[0], parse_item(ast[1:]))
        return {ast[0]: _dict(ast[1:])}
    
    
    if ast[0] in {"STRING", "REGEX"}:
        return {ast[0]: ast[1]}
    if ast[0] in {"SUBTAG", "SUBTYPE"}:
        return {ast[0]: dict(ast[1:])}
    elif ast[0] in {"OPT", "NOT", "EXACT"}:
        return {ast[0]: generate_dict_structure(ast[1])}
    if ast[0] == "TAG":
        return parse_tag(ast)
    elif ast[0] in IDENT_TYPES:
        return parse_item(ast)
    elif ast[0] == "AND":
        left  = generate_dict_structure(ast[1])
        right = generate_dict_structure(ast[2])
        return {"AND": [left, right]}
    elif ast[0] == "OR":
        left  = generate_dict_structure(ast[1])
        right = generate_dict_structure(ast[2])
        return {"OR": [left, right]}
    elif ast[0] == "EXPR":
        return generate_dict_structure(ast[1])

    raise ValueError(f"Unexpected AST node: {ast}")


def flatten_dict_structure(d: dict) -> dict:
    def fix_and(d):
        ands = [True]
        if "AND" in d:
            while ands:
                ands = []
                other = []
                for item in d["AND"]:
                    if "AND" in item:
                        ands.extend(item["AND"])
                    else:
                        other.append(item)
                d["AND"] = list(map(flatten_dict_structure, ands + other))
        return d

    def fix_or(d):
        ors = [True]
        # if "OR" in d:
        while ors:
            ors = []
            other = []
            for item in d["OR"]:
                if "OR" in item:
                    ors.extend(item["OR"])
                else:
                    other.append(item)
            d["OR"] = list(map(flatten_dict_structure, ors + other))
        return d

    if "OR" in d:
        d = fix_or(d)
    d = fix_and(d)
    return d
