# Parsing Notes

```bnf
<QUERY> ::= <QUERY>.<QUERY> | <QUERY>,<QUERY> | <EXPR>
<CONJ>  ::= "," | "."
<L>     ::= "{"
<R>     ::= "}"
<EXPR>  ::= <PREFIX><HEXPR> | <L><EXPR><R> | <L><HEXPR><CONJ><EXPR><R>
<HEXPR> ::= <ATOM> | <L><HEXPR><R> | <L><HEXPR><CONJ><HEXPR><R>
<BOOL_IDENT>  ::= <IDENT> | <NEG><IDENT>
<IDENT> ::= [A-Za-z0-9_]+

```

```txt
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
```