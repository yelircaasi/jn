'''
# Example usage
dsl_code1 = "{var1.var2},{var3.var4}"
dict_structure1 = dsl_to_dict(dsl_code1)
print(dict_structure1)  # Output should be: {"OR": [{"AND": ["var1", "var2"]}, {"AND": ["var3", "var4"]}]}

dsl_code2 = "x.{y,z}"
dict_structure2 = dsl_to_dict(dsl_code2)
print(dict_structure2)  # Output should be: {"AND": ["x", {"OR": ["y", "z"]}]}

dsl_code3 = "a.b,c.d"
dict_structure3 = dsl_to_dict(dsl_code3)
print(dict_structure3)  # Output should be: {"OR": [{"AND": ["a", "b"]}, {"AND": ["c", "d"]}]}

dsl_code4 = "a,b.c"
dict_structure4 = dsl_to_dict(dsl_code4)
print(dict_structure4)  # Output should be: {"OR": ["a", {"AND": ["b", "c"]}]}
'''

import re
from typing import Callable

from .item_parser import make_item_parser
from .subparsers import parse_homogeneous
from .lists import IDENT_TYPES, PREFIX_TO_TYPE
from .tokenizer import make_tokenizer
from .subparsers import non_tag_dispatcher

def parse_expression(tokens):
    
    def parse_primary(tokens):
        print('p')
        if not tokens:
            return None
        
        token = tokens.pop(0)

        if (toktype := token[0]) in IDENT_TYPES:
            print(toktype, token[1])
            if toktype == "IDENTIFIER":
                if tokens and tokens[0][0] == "BIND":
                    tokens.pop(0)
                    _, subtag = tokens.pop(0)
                    return ("TAG", ("STRING", token[1]), ("SUBTAG", ("STRING", subtag))) # queries of the type tag:{subtag1.subtag2} currenty note supported; instead tag:subtag1.tag:subtag2
                return ("TAG", ("STRING", token[1]))
        if toktype in non_tag_dispatcher:
            # expr = parse_homogeneous(tokens, PREFIX_TO_TYPE[toktype])
            expr = non_tag_dispatcher[toktype](tokens)
            return ("EXPR", expr)
        if token[0] == 'LBRACE':
            expr = parse_expression(tokens)
            if tokens and tokens[0][0] == 'RBRACE':
                tokens.pop(0)
            return ('EXPR', expr)
        
        raise SyntaxError(f"Unexpected token: {token}")

    def parse_and(tokens):
        print('a')
        left = parse_primary(tokens)
        while tokens and tokens[0][0] == 'AND':
            tokens.pop(0)
            right = parse_primary(tokens)
            left = ('AND', left, right)
        return left

    def parse_or(tokens):
        print('o')
        left = parse_and(tokens)
        while tokens and tokens[0][0] == 'OR':
            tokens.pop(0)
            right = parse_and(tokens)
            left = ('OR', left, right)
        return left

    return parse_or(tokens)


def generate_dict_structure(ast):
    def parse_tag(item: tuple[tuple[str, tuple[str, str]]]) -> dict[str, str]:
        d = {ast[0]: dict(ast[1:])}
        if "SUBTAG" in d["TAG"]:
            d["TAG"]["SUBTAG"] = dict((d["TAG"]["SUBTAG"],))
        return d

    def parse_item(item: tuple[tuple[str, tuple[str, str]]]) -> dict[str, str]:
        return {ast[0]: dict(ast[1:])}

    if ast[0] in {"STRING", "REGEX"}:
        return dict(ast)
    if ast[0] == "TAG":
        return parse_tag(ast)
    elif ast[0] in IDENT_TYPES:
        return parse_item(ast)
    elif ast[0] == 'AND':
        left = generate_dict_structure(ast[1])
        right = generate_dict_structure(ast[2])
        return {"AND": [left, right]}
    elif ast[0] == 'OR':
        left = generate_dict_structure(ast[1])
        right = generate_dict_structure(ast[2])
        return {"OR": [left, right]}
    elif ast[0] == 'EXPR':
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
    

def dsl_to_dict(dsl_code):
    tokenize = make_tokenizer(None)
    tokens = tokenize(dsl_code)
    ast = parse_expression(tokens)
    dict_structure = generate_dict_structure(ast)
    return dict_structure
