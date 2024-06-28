import re


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
        ('LBRACE', r'[\[|❨❪]'),        # Left bracket
        ('RBRACE', r'[\]❩❫]'),        # Right bracket
        ('AND', r'\.'),           # AND operator
        ('OR', r','),             # OR operator
        ('EXACTLY', r'~~'),
        ('NOT', r'~'),
        ('STRINGEMPTY', r'\?'),
        ('LPATH', r'@\['),
        ('RPATH', r'\]'),
        ('REGEX_OPEN', r'⸨'),
        ('REGEX_CLOSE', r'⸩'),
        ('REGEX', r'(?<=⸨)[^⸩]+'),
        ('BIND', r':'),
        ('PREFIX_ID', r'≡|󰻾'),
        ('PREFIX_TYPE', r'%'),
        ('PREFIX_STATUS', r'/'),
        ('PREFIX_EXTRA', r'\+'),
        ('PREFIX_LANGUAGE', r'€'),
        ('PREFIX_PROGLANG', r'_'), #r'…'),
        ('PREFIX_DATEMOD', r'\^'),
        ('PREFIX_RATING', r'\*|★'),
        ('PREFIX_CACHED', r'@'),
        ('PREFIX_DATECREATED', r'©'),
        ('IDENTIFIER', r'[A-Za-z][A-Za-z0-9_-]*'),
        ('DATE', r'\d{4}-\d\d-\d\d'),
        ('SKIP', r'[ \t⸩]+'),
        ('MISSTRING', r'.'),
        
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
