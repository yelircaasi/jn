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
    if tokens[0][0] == "LBRACE":
        tokens.pop(0)
        return parse_homogeneous(tokens, "STATUS")
    
    opt, neg = itemgetter("OPT", "NEG")(parse_modifiers(tokens))

    typ, status_string = tokens.pop(0)
    if typ == "IDENTIFIER":
        string_tuple = ("STRING", status_string)
    elif typ == "REGEX_EMBEDDED":
        string_tuple = ("REGEX", status_string)

    return {
        (True, True): ("OPT", ("NOT", string_tuple)),
        (True, False): ("OPT", string_tuple),
        (False, True): ("NOT", string_tuple),
        (False, False): string_tuple
    }[(opt, neg)]


def parse_extra(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    +extraAttrName:extraAttrValue
    """
    opt, neg, exact = itemgetter("OPT", "NEG", "EXACT")(parse_modifiers(tokens))
    
    typ, extra_name = tokens.pop(0)
    if typ == "IDENTIFIER":
        name_tuple = ("NAME", ("STRING", extra_name))
    elif typ == "REGEX_EMBEDDED":
        name_tuple = ("NAME", ("REGEX", extra_name))
    else:
        raise ValueError
    if tokens and tokens[0][0] == "BIND":
        tokens.pop(0)
        typ, extra_value = tokens.pop(0)
        if typ == "IDENTIFIER":
            value_tuple = ("VALUE", ("STRING", extra_value))
        elif typ == "REGEX_EMBEDDED":
            value_tuple = ("VALUE", ("REGEX", extra_value))
        extra_tuple = ("EXTRA", name_tuple, value_tuple)
    else:
        extra_tuple = ("EXTRA", name_tuple)

    return {
        (True, True): ("OPT", ("NOT", extra_tuple)),
        (True, False): ("OPT", extra_tuple),
        (False, True): ("NOT", extra_tuple),
        (False, False): extra_tuple
    }[(opt, neg)]    


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

    typ, val = tokens.pop(0)
    assert typ == "IDENTIFIER"
    language_tuple = ("EXTRA", ("NAME", ("STRING", "language")), ("VALUE", ("STRING", val)))

    return {
        (True, True): ("OPT", ("NOT", language_tuple)),
        (True, False): ("OPT", language_tuple),
        (False, True): ("NOT", language_tuple),
        (False, False): language_tuple
    }[(opt, neg)]

    if typ == "LBRACE":
        return parse_homogeneous(tokens, "LANGUAGE")


def parse_proglang(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    _python
    _{python.{haskell,rust}}
    """
    opt, neg, exact = itemgetter("OPT", "NEG", "EXACT")(parse_modifiers(tokens))

    typ, val = tokens.pop(0)
    assert typ == "IDENTIFIER"
    proglang_tuple = ("EXTRA",  ("NAME", ("STRING", "progLang")), ("VALUE", ("STRING", val)))

    return {
        (True, True): ("OPT", ("NOT", proglang_tuple)),
        (True, False): ("OPT", proglang_tuple),
        (False, True): ("NOT", proglang_tuple),
        (False, False): proglang_tuple
    }[(opt, neg)]

    if typ == "LBRACE":
        return parse_homogeneous(tokens, "PROGLANG")
    


def parse_rating(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    *A
    """
    opt, neg, exact = itemgetter("OPT", "NEG", "EXACT")(parse_modifiers(tokens))

    #-----
    _tuple = {
        (True, True): ("OPT", ("NOT", ("", ))),
        (True, False): ("OPT", ("STRING", )),
        (False, True): ("NOT", ("STRING", )),
        (False, False): ("STRING", )
    }[(opt, neg)]
    #-----
    
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

    #-----
    _tuple = {
        (True, True): ("OPT", ("NOT", ("", ))),
        (True, False): ("OPT", ("STRING", )),
        (False, True): ("NOT", ("STRING", )),
        (False, False): ("STRING", )
    }[(opt, neg)]
    #-----
    
    token = tokens.pop(0)
    return ("CACHED_QUERY", token[1])


def parse_date_created(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    ^2024-05-17
    ^~~2024-03-29
    ^~2023-12-13
    """
    opt, neg, exact = itemgetter("OPT", "NEG", "EXACT")(parse_modifiers(tokens))
    assert not (neg and exact)
    _, date = tokens.pop(0)
    date_tuple =  ("DATE", date)

    return {
        (False, False, False): ("DATE_CREATED", date_tuple, ("INTERPRETATION", "NEWER_THAN")),
        (False, False, True):  ("DATE_CREATED", date_tuple, ("INTERPRETATION", "EXACT")),
        (False, True, False):  ("DATE_CREATED", date_tuple, ("INTERPRETATION", "OLDER_THAN")),
        (False, True, True):   ("DATE_CREATED", date_tuple, ("INTERPRETATION", "EXCLUDE")),
        (True, False, False):  ("DATE_CREATED", ("OPT", date_tuple, ("INTERPRETATION", "NEWER_THAN"))),
        (True, False, True):   ("DATE_CREATED", ("OPT", date_tuple, ("INTERPRETATION", "EXACT"))),
        (True, True, False):   ("DATE_CREATED", ("OPT", date_tuple, ("INTERPRETATION", "OLDER_THAN"))),
        (True, True, True):    ("DATE_CREATED", ("OPT", date_tuple, ("INTERPRETATION", "EXCLUDE"))),
    }[(opt, neg, exact)]


def parse_date_modified(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    ^2024-05-17
    ^~~2024-03-29
    ^~2023-12-13
    """
    opt, neg, exact = itemgetter("OPT", "NEG", "EXACT")(parse_modifiers(tokens))
    assert not (neg and exact)
    _, date = tokens.pop(0)
    date_tuple =  ("DATE", date)

    return {
        (False, False, False): ("DATE_MODIFIED", date_tuple, ("INTERPRETATION", "NEWER_THAN")),
        (False, False, True):  ("DATE_MODIFIED", date_tuple, ("INTERPRETATION", "EXACT")),
        (False, True, False):  ("DATE_MODIFIED", date_tuple, ("INTERPRETATION", "OLDER_THAN")),
        (False, True, True):   ("DATE_MODIFIED", date_tuple, ("INTERPRETATION", "EXCLUDE")),
        (True, False, False):  ("DATE_MODIFIED", ("OPT", date_tuple, ("INTERPRETATION", "NEWER_THAN"))),
        (True, False, True):   ("DATE_MODIFIED", ("OPT", date_tuple, ("INTERPRETATION", "EXACT"))),
        (True, True, False):   ("DATE_MODIFIED", ("OPT", date_tuple, ("INTERPRETATION", "OLDER_THAN"))),
        (True, True, True):    ("DATE_MODIFIED", ("OPT", date_tuple, ("INTERPRETATION", "EXCLUDE"))),
    }[(opt, neg, exact)]


def parse_id(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """ """
    opt, neg, exact = itemgetter("OPT", "NEG", "EXACT")(parse_modifiers(tokens))

    #-----
    _tuple = {
        (True, True): ("OPT", ("NOT", ("", ))),
        (True, False): ("OPT", ("STRING", )),
        (False, True): ("NOT", ("STRING", )),
        (False, False): ("STRING", )
    }[(opt, neg)]
    #-----
    
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

    #-----
    _tuple = {
        (True, True): ("OPT", ("NOT", ("", ))),
        (True, False): ("OPT", ("STRING", )),
        (False, True): ("NOT", ("STRING", )),
        (False, False): ("STRING", )
    }[(opt, neg)]
    #-----
    
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
