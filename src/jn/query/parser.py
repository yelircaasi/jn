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

# Step 1: Tokenizer
def tokenize(dsl_code):
    # alias =  {
    #         "id": "=",
    #         "tag": "",
    #         "subtag": "_",
    #         "type": "%",
    #         "subtypeBinder": ":",
    #         "status": "/",
    #         "extra": "+",
    #         "language": "€",
    #         "progLang": "…",
    #         "rating": "*",
    #         "ratingExactnessModifier": "~~",
    #         "dateModified": "^",
    #         "cachedQuery": "@",
    #         "dateCreated": "©"

    #     }
    # identifier_start = "".join(set((
    #     alias["id"],
    #     alias["tag"],
    #     alias["subtag"],
    #     alias["type"],
    #     alias["status"],
    #     alias["extra"],
    #     alias["language"],
    #     alias["progLang"],
    #     alias["rating"],
    #     alias[],
    #     alias[],
    # )))
    # identifier_body = 

    token_specification = [
        ('LBRACE', r'\{'),        # Left bracket
        ('RBRACE', r'\}'),        # Right bracket
        ('AND', r'\.'),           # AND operator
        ('OR', r','),             # OR operator
        ('RATINGEXACT', r'~~'),
        ('EXACTLY', r'~~'),
        ('NOT', r'~'),
        ('STRINGEMPTY', r'\?'),
        ('LPATH', r'@\['),
        ('RPATH', r'\]'),
        ('REGEX_OPEN', r'⸨'),
        ('REGEX_CLOSE', r'⸩'),
        ('REGEX', r'(?<=⸨)[^⸩]+'),
        ('BIND', r':'),
        ('PREFIX_ID', r'\='),
        # ('PREFIX_SUBTAG', r'_'),
        ('PREFIX_TYPE', r'%'),
        ('PREFIX_STATUS', r'/'),
        ('PREFIX_EXTRA', r'\+'),
        ('PREFIX_LANGUAGE', r'€'),
        ('PREFIX_PROGLANG', r'_'), #r'…'),
        ('PREFIX_DATEMOD', r'\^'),
        ('PREFIX_RATING', r'\*'),
        ('PREFIX_CACHED', r'@'),
        ('PREFIX_DATECREATED', r'©'),
        ('IDENTIFIER', r'[A-Za-z][A-Za-z0-9_-]*'),  # Identifiers
        ('DATE', r'\d{4}-\d\d-\d\d'),
        # ('IDENTIFIER', f'[=%+*^a-z_/€…~@©]~{0,2}[A-Za-z0-9:_-]*|⸨[^⸩]+'),  # Identifiers
        # ('IDENTIFIER', r'[=%+*^a-z_/€…~@©]~{0,2}[A-Za-z0-9:_-]*|⸨[^⸩]+'),  # Identifiers
        # ('IDENTIFIER', r'[\=\%\+\*\^a-z_/€…~@©]~{0,2}[A-Za-z0-9:_-]*|⸨[^⸩]+'),  # Identifiers
        ('SKIP', r'[ \t⸩]+'),      # Skip over spaces and tabs
        
        ('MISSTRING', r'.'),       # Any other character
        
    ]
    token_regex = re.compile('|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification), re.UNICODE)
    tokens = []
    for mo in re.finditer(token_regex, dsl_code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'SKIP':
            continue
        elif kind == 'MISSTRING':
            raise RuntimeError(f'Unexpected character: {value}')
        tokens.append((kind, value))
    return tokens


IDENT_TYPES = {
        "IDENTIFIER",
        "TAG",
        'RATINGEXACT',
        'NOT',
        'STRINGEMPTY',
        'LPATH',
        'RPATH',
        'REGEX_OPEN',
        'REGEX_CLOSE',
        'REGEX',
        'BIND',
        'ID',
        'SUBTAG',
        'TYPE',
        'STATUS',
        'EXTRA',
        'LANGUAGE',
        'PROGLANG',
        'DATEMOD',
        'RATING',
        'CACHED',
        'DATECREATED',
        'DATE',
    }
PREFIX_TO_TYPE = {
        'PREFIX_ID': "ID",
        'PREFIX_SUBTAG': "SUBTAG",
        'PREFIX_TYPE': "TYPE",
        'PREFIX_STATUS': "STATUS",
        'PREFIX_EXTRA': "EXTRA",
        'PREFIX_LANGUAGE': "LANGUAGE",
        'PREFIX_PROGLANG': "PROGLANG",
        'PREFIX_DATEMOD': "DATEMOD",
        'PREFIX_RATING': "RATING",
        'PREFIX_CACHED': "CACHED",
        'PREFIX_DATECREATED': "DATECREATED",
}



# Step 2: Parser with Precedence




def parse_expression(tokens):
    
    def parse_primary(tokens):
        if not tokens:
            return None
        
        token = tokens.pop(0)

        if (toktype := token[0]) in IDENT_TYPES:
            print(toktype)
            if toktype == "IDENTIFIER":
                if tokens and tokens[0][0] == "BIND":
                    tokens.pop(0)
                    _, subtag = tokens.pop(0)
                    return ("TAG", ("STRING", token[1]), ("SUBTAG", ("STRING", subtag))) # queries of the type tag:{subtag1.subtag2} currenty note supported; instead tag:subtag1.tag:subtag2
                return ("TAG", ("STRING", token[1]))
        if toktype in PREFIX_TO_TYPE:
            expr = parse_homogeneous(tokens, PREFIX_TO_TYPE[toktype])
            return ("EXPR", expr)
        if token[0] == 'LBRACE':
            expr = parse_expression(tokens)
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
    tokens = tokenize(dsl_code)
    ast = parse_expression(tokens)
    dict_structure = generate_dict_structure(ast)
    return dict_structure
