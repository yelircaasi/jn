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
            ("REGEX_FULL_OPEN",  r"⦃|\[\["),
            ("REGEX_FULL_CLOSE", r"⦄|\]\]"),
            ("REGEX_EMBEDDED_OPEN", r"〈"),
            ("REGEX_EMBEDDED_CLOSE", r"〉"),
            ("REGEX_TEXT_OPEN", r"⸨"),
            ("REGEX_TEXT_CLOSE", r"⸩"),
            ("REGEX_LINK_OPEN", r"«"),
            ("REGEX_LINK_CLOSE", r"»"),
            ("REGEX_FULL", r"(?<=⦃).+?(?=⦄)|(?<=\[\[).+?(?=\]\])"),
            ("REGEX_EMBEDDED", r"(?<=〈)[^〉]+"),
            ("REGEX_TEXT", r"(?<=⸨)[^⸩]+"),
            ("REGEX_LINK", r"(?<=«)[^»]+"),
            ("LBRACE", f"[{leftsquare}{leftround}{leftcurved}]"),
            ("DATE", r"\d{4}-\d\d-\d\d"),
            ("NUMBER", r"(?<=[\*~\?])-?\d\.\d+|(?<=[\*~])-?\d(?=[^\.])|(?<=[\*~])-?\d(?=\.[^\d])"),
            ("RBRACE", r"[\]❩❫]"),  # Right bracket
            ("AND", r"\."),  # AND operator
            ("OR", r","),  # OR operator
            ("EXACTLY", r"~~"),
            ("NOT", r"[~󱈸]"),
            ("OPT", r"\?"),
            ("LPATH", r"❮"),
            ("RPATH", r"❯"),
            ("PREFIX_ID", r"ID::|≡|󰻾"),
            ("PREFIX_TYPE", r"TYPE::|%"),
            ("PREFIX_STATUS", r"STATUS::|/"),
            ("PREFIX_EXTRA", r"EXTRA::|\+"),
            ("PREFIX_LANGUAGE", r"LANGUAGE::|€"),
            ("PREFIX_PROGLANG", r"PROGLANG::|❱"),  # r'…'),
            ("PREFIX_DATE_MODIFIED", r"DATE_MODIFIED::|\^"),
            ("PREFIX_RATING", r"RATING::|\*|★"),
            ("PREFIX_CACHED", r"CACHED::|@"),
            ("PREFIX_DATE_CREATED", r"DATE_CREATED::|©"),
            ("IDENTIFIER", r"[A-Za-z][A-Za-z0-9_-]*"),
            ("BIND", r":"),
            ("SKIP", r"[ \t]+"),
            ("MISSTRING", r"."),
        ]
        token_regex = re.compile("|".join(f"(?P<{pair[0]}>{pair[1]})" for pair in token_specification), re.UNICODE)
        tokens = []
        for mo in re.finditer(token_regex, dsl_code):
            kind = mo.lastgroup
            value = mo.group()
            if kind == "SKIP":
                continue
            elif kind == "MISSTRING":
                raise RuntimeError(f"Unexpected character: {value}")
            tokens.append((kind, value))
        return tokens

    return tokenize
