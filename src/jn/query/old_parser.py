"""
{x,y,z}.{a,b}
td = {
    "AND": [
        {"OR": ["x", "y", "z"]},
        {"OR": ["a", "b"]}
    ]
}


note = {"tags": ["a", "x"]}
note = {"tags": ["a", "b"]}
"""

'''
Characters not treated as special characters by Bash:
A-Za-z % - _ ~ ^ @ [ ] { } : , . / ? +

NEW CONSIDERATIONS =============================================
bash special characters not allowed; neither are spaces
structural characters in the query language are { } , . : 
: should be reserved for binding attribute names to values, such as type:book
_ and - would be nice to have as valid non-initial identifier characters; identifiers must start with a letter (or number?)
support character sets from other languages, such as cyrillic
only tags start with [A-Za-z]
_ for subtags
~ for negation
= for id
@ to reference saved queries
/ for status
+ to prefix extra attributes
^ for date
* for rating (allowing ~~ for exact; default is *5 for geq 5 and *~5 for leq 5)
% for type, with : inside 
] for subtype (or ﹪)
€ for (human) language
… for programming language

other unicode characters?

? allow matching 'empty' values, such as None or ""

Examples: 

consilium edit {@biologyTop,philosophy,neuroscience}.^2023-01-01.*5.{%book,%idea,%site}
================================================================
Crazy idea: use Greek letters:
Α α, Β β, Γ γ, Δ δ, Ε ε, Ζ ζ, Η η, Θ θ, Ι ι, Κ κ, Λ λ, Μ μ, Ν ν, Ξ ξ, Ο ο, Π π, Ρ 
ρ rating
, Σ 
σ status
/ς
, Τ 
τ type, 
Υ υ, Φ φ, Χ χ, Ψ ψ, Ω ω.
================================================================

(rejected: --additional_argument bound to value with non non-space non-alphanumeric character)
-> instead: use environment variables, all of which are optional

MAYBE LATER:
@[] to reference the path to a file -> assumed to be relative if not starting with / ; ~ allowed and . not allowed; _/ refers to query_files in nots directory


@[...] to refer to the contents of a path
~ negation
[...] - regex search within string: ?tag[regex],tag2[regex2]

?@savedTagQueryAlias
=@savedSetAlias

@savedQueryAlias

=id1,id2,id3def condition_from_string(s: str) -> Callable[[dict], bool]:
    # to be fully implemented for all attributes later; just tags for now
    def inner(d: dict):
        return s in d["tags"]
    
    return inner


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
=[regex for id]
:type
:type:subtype
::type:subtype or empty type
:type::subtype - type and subtype or empty subtype

%status
%%status or empty

*rating above
*~rating below
**rating or empty


[substring/regex in text]
[substring/regex in text, case insensitive]i
{substring/regex in link}
{substring/regex in link, case insensitive}i

^DDDD-DD-DD - oldest date modified
^^DDDD-DD-DD - oldest date created
^~DDDD-DD-DD - newest date modified
^^~DDDD-DD-DD - newest date created

+extraTag:value
++extraTag:value or empty


?tag.tag.tag:subtag.subtag.subtag
  . OR operator for tags
  , OR operator for tags
  {...} for tag grouping, but for now give
  
AND precedence over OR, 
    requiring more work on the user's end for simpler implementation.
  ~ for tag negation
  example: @tag1.tag2,tag3.tag4

_language
__language or empty value for language


Tentative:

]progLang (need to change to camel case)
]]fileType
'''

import re
from typing import Callable

# from .item_parser import make_item_parser
make_item_parser = None

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
        ('NOT', r'~'),
        ('MATCHEMPTY', r'\?'),
        ('LPATH', r'@\['),
        ('RPATH', r'\]'),
        ('REGEXOPEN', r'｟'),
        ('REGEXCLOSE', r'｠'),
        ('REGEX', r'(?<=｟)[^｠]+'),
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
        # ('IDENTIFIER', f'[=%+*^a-z_/€…~@©]~{0,2}[A-Za-z0-9:_-]*|｟[^｠]+'),  # Identifiers
        # ('IDENTIFIER', r'[=%+*^a-z_/€…~@©]~{0,2}[A-Za-z0-9:_-]*|｟[^｠]+'),  # Identifiers
        # ('IDENTIFIER', r'[\=\%\+\*\^a-z_/€…~@©]~{0,2}[A-Za-z0-9:_-]*|｟[^｠]+'),  # Identifiers
        ('SKIP', r'[ \t｠]+'),      # Skip over spaces and tabs
        
        ('MISMATCH', r'.'),       # Any other character
        
    ]
    token_regex = re.compile('|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification), re.UNICODE)
    tokens = []
    for mo in re.finditer(token_regex, dsl_code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Unexpected character: {value}')
        tokens.append((kind, value))
    return tokens


IDENT_TYPES = {
        "IDENTIFIER",
        'RATINGEXACT',
        'NOT',
        'MATCHEMPTY',
        'LPATH',
        'RPATH',
        'REGEXOPEN',
        'REGEXCLOSE',
        'REGEX',
        'BIND',
        'PREFIX_ID',
        'PREFIX_SUBTAG',
        'PREFIX_TYPE',
        'PREFIX_STATUS',
        'PREFIX_EXTRA',
        'PREFIX_LANGUAGE',
        'PREFIX_PROGLANG',
        'PREFIX_DATEMOD',
        'PREFIX_RATING',
        'PREFIX_CACHED',
        'PREFIX_DATECREATED',
        'DATE'
    }
PREFIX_TYPES = {
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

def parse_homogeneous(tokens, attr):
    ...
    # need to make a sub-parser for single-attribute expressions like %{xxx,yyy,zzz.aaa}

def parse_expression(tokens):
    
    def parse_primary(tokens):
        if not tokens:
            return None
        
        token = tokens.pop(0)
        if token[0] in IDENT_TYPES:
            # return ('IDENTIFIER', token[1])
            new_tokens = [token]
            while tokens and tokens[0][0] in IDENT_TYPES:
                token = tokens.pop(0)
                new_tokens.append(token)
                # print(new_tokens)
            return tuple(new_tokens)
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
    def parse_item(item: tuple[tuple[str, str]]) -> dict[str, str]:
        return dict(item)
    
    if ast[0][0] in IDENT_TYPES:
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

# Putting it all together
def dsl_to_dict(dsl_code):
    print(dsl_code)
    print()
    tokens = tokenize(dsl_code)
    print(tokens)
    print()
    ast = parse_expression(tokens)
    print(ast)
    print()
    dict_structure = generate_dict_structure(ast)
    print(dict_structure)
    print()
    return dict_structure

q = "tagA,｟^In the beginning｠.{tagB,tagC}.{tagD,{tagE.tagF.tagG}}"
dsl_to_dict(q)
q = "=idA,asdf,｟^In the beginning｠._subtagA,%typeA:subtypeC,/status,+extraA,€EN,…python,*~~ratingB,*ratingA,^2024-05-07,@cached,©2021-04-04"
dsl_to_dict(q)
q = "%software.noteManagement._appFlowy.*A"
dsl_to_dict(q)

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

# def condition_from_string(s: str) -> Callable[[dict], bool]:
#     # to be fully implemented for all attributes later; just tags for now
#     def inner(d: dict):
#         return s in d["tags"]
    
#     return inner

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
        ('MISMATCH', r'.'),       # Any other character
    ]
    token_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)
    tokens = []
    for mo in re.finditer(token_regex, dsl_code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
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