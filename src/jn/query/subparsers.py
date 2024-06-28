import re


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
            return ((attr, ("REGEX", token[1])))
            

        elif token[0] == 'LBRACE':
            expr = parse_homogeneous(tokens, attr)
            if tokens and tokens[0][0] == 'RBRACE':
                tokens.pop(0)
            return ('EXPR', expr)
        raise SyntaxError(f"Unexpected token: {token}")

    def parse_and(tokens):
        left = parse_primary(tokens)
        while tokens and tokens[0][0] == 'AND':
            tokens.pop(0)
            right = parse_primary(tokens)
            left = ('AND', left, right)
        return left

    def parse_or(tokens):
        left = parse_and(tokens)
        while tokens and tokens[0][0] == 'OR':
            tokens.pop(0)
            right = parse_and(tokens)
            left = ('OR', left, right)
        return left

    return parse_or(tokens)


def parse_date_modified(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    ^2024-05-17
    ^~~2024-03-29
    ^~2023-12-13
    """
    token = token.pop(0)
    typ = token[0]
    if typ == "DATE":
        return ("DATE_MODIFIED", ("DATE", token[1]), ("INTERPRETATION", "OLDEST"))
    if typ == "NOT":
        token = token.pop(0)
        return ("DATE_MODIFIED", ("DATE", token[1]), ("INTERPRETATION", "NEWEST"))
    if typ == "EXACTLY":
        return ("DATE_MODIFIED", ("DATE", token[1]), ("INTERPRETATION", "EXACT"))



def parse_regex(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    ⸨^expression\shere⸩
    """
    ret = tokens.pop(0)
    tokens.pop(0)
    return ret


def parse_status(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    
    """
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
    toktype, name = tokens.pop(0)
    assert toktype == "IDENTIFIER"
    toktype, bind = tokens.pop(0)
    assert toktype == "BIND"
    tokype, value = tokens.pop(0)
    return ("EXTRA", ("NAME", name), ("STRING", value))


def parse_type(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    %type
    %type:subtype
    """
    print(tokens)
    toktype, type_string = tokens.pop(0)
    assert toktype == "IDENTIFIER"
    if tokens and tokens[0][0] == "BIND":
        tokens.pop(0)
        toktype, subtype_string = tokens.pop(0)
        assert toktype == "IDENTIFIER"
        return ("TYPE", ("STRING", type_string), ("SUBTYPE", ("STRING", subtype_string)))
    return ("TYPE", ("STRING", type_string))


def parse_language(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    €EN
    €{EN,DE,FR}
    """
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
    token = tokens.pop(0)
    typ = token[0]
    if typ == "IDENTIFIER":
        return ("RATING", ("STRING", token[1]))
    if typ == "LBRACE":
        return parse_homogeneous(tokens, "RATING")
    raise ValueError


def parse_cached(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    @queryName
    """
    token = tokens.pop(0)
    return ("CACHED_QUERY", token[1])
    


def parse_date_created(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    ^2024-05-17
    ^~~2024-03-29
    ^~2023-12-13
    """
    token = token.pop(0)
    typ = token[0]
    if typ == "DATE":
        return ("DATE_CREATED", ("DATE", token[1]), ("INTERPRETATION", "OLDEST"))
    if typ == "NOT":
        token = token.pop(0)
        return ("DATE_CREATED", ("DATE", token[1]), ("INTERPRETATION", "NEWEST"))
    if typ == "EXACTLY":
        return ("DATE_CREATED", ("DATE", token[1]), ("INTERPRETATION", "EXACT"))
    

def parse_id(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    
    """
    token = tokens.pop(0)
    typ = token[0]
    if typ == "ID":
        return ("ID", ("STRING", token[1]))
    if typ == "LBRACE":
        return parse_homogeneous(tokens, "ID")
    raise ValueError


def parse_id(tokens: list[tuple[str, str]]) -> tuple[tuple]:
    """
    
    """
    token = tokens.pop(0)
    typ = token[0]
    if typ == "ID":
        return ("ID", ("STRING", token[1]))
    if typ == "LBRACE":
        return parse_homogeneous(tokens, "ID")
    raise ValueError


def parse_tag():
    ...


non_tag_dispatcher = {
        'PREFIX_ID':          parse_id,
        'PREFIX_TYPE':        parse_type,
        'PREFIX_STATUS':      parse_status,
        'PREFIX_EXTRA':       parse_extra,
        'PREFIX_LANGUAGE':    parse_language,
        'PREFIX_PROGLANG':    parse_proglang,
        'PREFIX_DATEMOD':     parse_date_modified,
        'PREFIX_RATING':      parse_rating,
        'PREFIX_CACHED':      parse_cached,
        'PREFIX_DATECREATED': parse_date_created,
}