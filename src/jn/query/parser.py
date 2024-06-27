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
        ('PREFIX_SUBTAG', r'_'),
        ('PREFIX_TYPE', r'%'),
        ('PREFIX_STATUS', r'/'),
        ('PREFIX_EXTRA', r'\+'),
        ('PREFIX_LANGUAGE', r'€'),
        ('PREFIX_PROGLANG', r'…'),
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
            # return ('IDENTIFIER', token[1])
            if toktype == "IDENTIFIER":
                if tokens and tokens[0][0] == "BIND":
                    tokens.pop(0)
                    _, subtag = tokens.pop(0)
                    return ("TAG", ("STRING", token[1]), ("SUBTAG", subtag))
                return ("TAG", ("STRING", token[1]))
        if toktype in PREFIX_TO_TYPE:
            expr = parse_homogeneous(tokens, PREFIX_TO_TYPE[toktype])
            # expr = non_tag_dispatcher[toktype](tokens)
            return ("EXPR", expr)
            

        # new_tokens = [token]
        # while tokens and tokens[0][0] in IDENT_TYPES:
        #         token = tokens.pop(0)
        #         new_tokens.append(token)
        #         # print(new_tokens)
        #     return tuple(new_tokens)
        elif token[0] == 'LBRACE':
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




# Step 3: Dictionary Construction
def generate_dict_structure(ast):
    def parse_item(item: tuple[tuple[str, tuple[str, str]]]) -> dict[str, str]:
        d = {}
        d.update({ast[0]: dict(ast[1:])})
        return d

    if ast[0] in {"STRING", "REGEX"}:
        return dict(ast)
    
    
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
    

    

# Putting it all together
def dsl_to_dict(dsl_code):
    tokens = tokenize(dsl_code)
    ast = parse_expression(tokens)
    dict_structure = generate_dict_structure(ast)
    return dict_structure

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

def make_condition_from_dict(config: ...) -> Callable:

    condition_from_string = make_item_parser(config)

    def condition_from_dict(query_tree: dict) -> Callable:
        def condition_from_element(element: str | dict) -> Callable[[dict], bool]:
            if isinstance(element, str):
                return condition_from_string(element)
            elif isinstance(element, dict):
                return condition_from_dict(element)
        
        if "AND" in query_tree:
            return lambda d: all(map(lambda f: f(d), map(condition_from_element, query_tree["AND"])))
        elif "OR" in query_tree:
            return lambda d: any(map(lambda f: f(d), map(condition_from_element, query_tree["OR"])))
        else:
            raise ValueError
        
    return condition_from_dict




""" PARSING WITH PRECEDENCE
What if I want to implement precedence? AND should always have precedence over OR in the absence of brackets.
ChatGPT

To implement precedence where AND has a higher precedence than OR, we need to adjust the parsing logic to handle operator precedence correctly. We'll use a recursive descent parser to ensure that AND operations are grouped more tightly than OR operations.
Implementation Steps

    Tokenizer: We'll use the same tokenizer as before to split the input into tokens.
    Parser: We'll modify the parser to respect operator precedence, ensuring that AND operations are evaluated before OR operations.
    Dictionary Construction: Convert the AST into the desired dictionary format.

Implementation in Python

Here’s how you can achieve this:

python

import re

# Step 1: Tokenizer
def tokenize(dsl_code):
    token_specification = [
        ('LBRACE', r'\{'),        # Left bracket
        ('RBRACE', r'\}'),        # Right bracket
        ('AND', r'\.'),           # AND operator
        ('OR', r','),             # OR operator
        ('IDENTIFIER', r'[a-z][A-Za-z]*'),  # Identifiers
        ('SKIP', r'[ \t]+'),      # Skip over spaces and tabs
        ('MISSTRING', r'.'),       # Any other character
    ]
    token_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)
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

# Step 2: Parser with Precedence
def parse(tokens):
    def parse_primary(tokens):
        if not tokens:
            return None
        
        token = tokens.pop(0)
        if token[0] == 'IDENTIFIER':
            return ('IDENTIFIER', token[1])
        elif token[0] == 'LBRACE':
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

# Step 3: Dictionary Construction
def generate_dict_structure(ast):
    if ast[0] == 'IDENTIFIER':
        return ast[1]
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

# Putting it all together
def dsl_to_dict(dsl_code):
    tokens = tokenize(dsl_code)
    ast = parse(tokens)
    dict_structure = generate_dict_structure(ast)
    return dict_structure

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

Explanation

    Tokenizer: The tokenize function splits the input into tokens, recognizing identifiers, brackets, and operators.
    Parser with Precedence: The parse function now respects operator precedence by splitting the parsing into multiple functions:
        parse_primary: Parses identifiers and expressions within brackets.
        parse_and: Ensures AND operations are parsed with higher precedence.
        parse_or: Ensures OR operations are parsed with lower precedence than AND.
    Dictionary Construction: The generate_dict_structure function traverses the AST to construct a nested dictionary representing the boolean logic.

This implementation respects the precedence of AND over OR, as specified, and should correctly transform your DSL into the desired dictionary format. Adjustments can be made for more complex DSL structures or additional features.

"""