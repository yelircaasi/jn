import json

from .parser import make_tokenizer, parse_expression, generate_dict_structure, flatten_dict_structure



def parse_query(query: str) -> None:
    tokenize = make_tokenizer(None) # TODO: config
    print(query)
    print()
    tokens = tokenize(query)
    print(tokens)
    print()
    parsed = parse_expression(tokens)
    print(parsed)
    print()
    generated = generate_dict_structure(parsed)
    print(json.dumps(generated, ensure_ascii=False, indent=4))
    print()
    flattened = flatten_dict_structure(generated)
    print(json.dumps(flattened, ensure_ascii=False, indent=4))
    print()
