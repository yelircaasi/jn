import re
from typing import Callable


def make_tokenizer(tokenizer_config) -> Callable[[str], list[tuple[str, str]]]:
    def escape_special(s: str) -> str:
        ...
        return s

    def tokenize(dsl_code):
        leftsquare = r"\\" + "["
        leftround = "❨"
        leftcurved = "❪"

        token_specification = [
            ('LBRACE', f'[{leftsquare}{leftround}{leftcurved}]'),
            ('RBRACE',    r'[\]❩❫]'),        # Right bracket
            ('AND', r'\.'),           # AND operator
            ('OR', r','),             # OR operator
            ('EXACTLY', r'~~'),
            ('NOT', r'[~󱈸]'),
            ('STRINGEMPTY', r'\?'),
            ('LPATH', r'❮'),
            ('RPATH', r'❯'),
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

    return tokenize


