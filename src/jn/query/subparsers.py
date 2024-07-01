from operator import itemgetter
import re


def parse_modifiers(tokens: list[tuple[str, str]]) -> dict[str, bool]:
    mods = {"EXACT": False, "OPT": False, "NEG": False}
    if not tokens:
        return mods
    while tokens[0][0] not in {"IDENTIFIER", "NUMBER", "DATE"}:
        typ, val = tokens.pop(0)

        if typ == "NOT":
            mods["NEG"] = True
        elif typ == "EXACTLY":
            mods["EXACT"] = True
        elif typ == "OPT":
            mods["OPT"] = True
        else:
            raise ValueError(f"Token type {typ} invalid at the start of a query atom.")
    return mods
    



def parse_homogeneous(tokens, attr):
    # need to make a sub-parser for single-attribute expressions like %{xxx,yyy,zzz.aaa}
    def parse_primary(tokens):
        if not tokens:
            return None

        token = tokens.pop(0)
        if token[0] == "IDENTIFIER":
            return (attr, ("STRING", token[1]))
        elif token[0] == "REGEX_OPEN":
            token = tokens.pop(0)
            tokens.pop(0)
            return (attr, ("REGEX", token[1]))

        elif token[0] == "LBRACE":
            expr = parse_homogeneous(tokens, attr)
            if tokens and tokens[0][0] == "RBRACE":
                tokens.pop(0)
            return ("EXPR", expr)
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


def parse_bare_regex(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    
    """
    typ, val = tokens.pop(0)
    



def parse_regex(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    ⸨^expression\shere⸩
    """
    ret = tokens.pop(0)
    tokens.pop(0)
    return ret


def parse_status(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """ """
    opt, neg, exact = itemgetter("OPT", "NEG", "EXACT")(parse_modifiers(tokens))

    token = tokens.pop(0)
    typ = token[0]
    if typ == "IDENTIFIER":
        return ("STATUS", ("STRING", token[1]))
    if typ == "LBRACE":
        return parse_homogeneous(tokens, "STATUS")
    raise ValueError


def parse_extra(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    +extraAttrName:extraAttrValue
    """
    opt, neg, exact = itemgetter("OPT", "NEG", "EXACT")(parse_modifiers(tokens))
    
    toktype, name = tokens.pop(0)
    assert toktype == "IDENTIFIER"
    if tokens and tokens[0][0] == "BIND":
        toktype, bind = tokens.pop(0)
        tokype, value = tokens.pop(0)
        return ("EXTRA", ("NAME", name), ("STRING", value))
    return ("EXTRA", ("NAME", name))
    


def parse_type(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    %type
    %type:subtype
    """
    opt, neg, _ = itemgetter("OPT", "NEG", "EXACT")(parse_modifiers(tokens))

    toktype, type_string = tokens.pop(0)
    assert toktype == "IDENTIFIER"
    
    type_tuple = {
        (True, True): ("OPT", ("NOT", ("STRING", type_string))),
        (True, False): ("OPT", ("STRING", type_string)),
        (False, True): ("NOT", ("STRING", type_string)),
        (False, False): ("STRING", type_string)
    }[(opt, neg)]
    
    subtype = None
    if tokens and tokens[0][0] == "BIND":
        tokens.pop(0)
        opt, neg, _ = itemgetter("OPT", "NEG", "EXACT")(parse_modifiers(tokens))
        toktype, subtype_string = tokens.pop(0)
        assert toktype == "IDENTIFIER"

        subtype = {
            (True, True): ("SUBTYPE", ("OPT", ("NOT", ("STRING", subtype_string)))),
            (True, False): ("SUBTYPE", ("OPT", ("STRING", subtype_string))),
            (False, True): ("NOT", ("SUBTYPE", ("STRING", subtype_string))),
            (False, False): ("SUBTYPE", ("STRING", subtype_string))
        }[(opt, neg)]

    return ("TYPE", type_tuple, subtype) if subtype else ("TYPE", type_tuple)


def parse_language(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    €EN
    €{EN,DE,FR}
    """
    opt, neg, exact = itemgetter("OPT", "NEG", "EXACT")(parse_modifiers(tokens))
    
    token = tokens.pop(0)
    typ = token[0]
    if typ == "IDENTIFIER":
        return ("LANGUAGE", ("STRING", token[1]))
    if typ == "LBRACE":
        return parse_homogeneous(tokens, "LANGUAGE")
    raise ValueError


def parse_proglang(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    _python
    _{python.{haskell,rust}}
    """
    opt, neg, exact = itemgetter("OPT", "NEG", "EXACT")(parse_modifiers(tokens))
    
    token = tokens.pop(0)
    typ = token[0]
    if typ == "IDENTIFIER":
        return ("PROGLANG", ("STRING", token[1]))
    if typ == "LBRACE":
        return parse_homogeneous(tokens, "PROGLANG")
    raise ValueError


def parse_rating(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    *A
    """
    opt, neg, exact = itemgetter("OPT", "NEG", "EXACT")(parse_modifiers(tokens))
    
    token = tokens.pop(0)
    typ = token[0]
    if typ == "NUMBER":
        return ("RATING", ("STRING", token[1]))
    # if typ == "LBRACE":
    #     return parse_homogeneous(tokens, "RATING")
    raise ValueError


def parse_cached(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    @queryName
    """
    opt, neg, exact = itemgetter("OPT", "NEG", "EXACT")(parse_modifiers(tokens))
    
    token = tokens.pop(0)
    return ("CACHED_QUERY", token[1])


def parse_date_created(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    ^2024-05-17
    ^~~2024-03-29
    ^~2023-12-13
    """
    opt, neg, exact = itemgetter("OPT", "NEG", "EXACT")(parse_modifiers(tokens))
    
    typ, val = tokens.pop(0)
    if typ == "DATE":
        return ("DATE_CREATED", ("DATE", val), ("INTERPRETATION", "OLDEST"))
    if typ == "NOT":
        token = token.pop(0)
        return ("DATE_CREATED", ("DATE", val), ("INTERPRETATION", "NEWEST"))
    if typ == "EXACTLY":
        return ("DATE_CREATED", ("DATE", val), ("INTERPRETATION", "EXACT"))


def parse_date_modified(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    ^2024-05-17
    ^~~2024-03-29
    ^~2023-12-13
    """
    opt, neg, exact = itemgetter("OPT", "NEG", "EXACT")(parse_modifiers(tokens))
    
    typ, val = tokens.pop(0)
    if typ == "DATE":
        return ("DATE_MODIFIED", ("DATE", val), ("INTERPRETATION", "OLDEST"))
    if typ == "NOT":
        _, val = tokens.pop(0)
        return ("DATE_MODIFIED", ("DATE", val), ("INTERPRETATION", "NEWEST"))
    if typ == "EXACTLY":
        _, val = tokens.pop(0)
        return ("DATE_MODIFIED", ("DATE", val), ("INTERPRETATION", "EXACT"))


def parse_id(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """ """
    opt, neg, exact = itemgetter("OPT", "NEG", "EXACT")(parse_modifiers(tokens))
    
    token = tokens.pop(0)
    typ = token[0]
    if typ == "ID":
        return ("ID", ("STRING", token[1]))
    if typ == "LBRACE":
        return parse_homogeneous(tokens, "ID")
    raise ValueError


def parse_id(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """ """
    opt, neg, exact = itemgetter("OPT", "NEG", "EXACT")(parse_modifiers(tokens))
    
    token = tokens.pop(0)
    typ = token[0]
    if typ == "ID":
        return ("ID", ("STRING", token[1]))
    if typ == "LBRACE":
        return parse_homogeneous(tokens, "ID")
    raise ValueError


def parse_tag(): ...


non_tag_dispatcher = {
    "PREFIX_ID": parse_id,
    "PREFIX_TYPE": parse_type,
    "PREFIX_STATUS": parse_status,
    "PREFIX_EXTRA": parse_extra,
    "PREFIX_LANGUAGE": parse_language,
    "PREFIX_PROGLANG": parse_proglang,
    "PREFIX_DATE_MODIFIED": parse_date_modified,
    "PREFIX_RATING": parse_rating,
    "PREFIX_CACHED": parse_cached,
    "PREFIX_DATE_CREATED": parse_date_created,
}
