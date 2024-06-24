"""
{'OR': ['tagA',
  {'AND': [
    {'AND': ['｟^In\\sthe\\sbeginning', {'OR': ['tagB', 'tagC']}]},
    {'OR': [
      'tagD', 
      {'AND': [
        {'AND': ['tagE', 'tagF']}, 
        'tagG']}]}]}
  ]
}
"""

index_dict = {
    "tagA": ["fileZ", "fileA", "fileY"],
    "tagB": ["fileA", "fileD", "fileE", "fileC"],
    "tagC": ["fileB", "fileE", "fileD"],
    "tagD": ["fileA", "fileC", "fileD", "fileB"],
    "tagE": ["fileB", "fileC", "fileD"],
    "tagF": ["fileB", "fileE", "fileD"],
    "tagG": ["fileB", "fileC", "fileD"],
    "｟^In\\sthe\\sbeginning": ["fileB", "fileC", "fileF"],
}


def get_files(parse_item: dict | str, index_dict: dict) -> list[str]:
    def get_files_from_or(or_list: list[str | dict]) -> set[str]:
        return set.union(*map(set, filter(lambda x: x is not None, map(lambda x: get_files(x, index_dict), or_list))))
        
    def get_files_from_and(and_list: list[str | dict]) -> list[str]:
        return set.intersection(*map(set, filter(lambda x: x is not None, map(lambda x: get_files(x, index_dict), and_list))))

    if isinstance(parse_item, dict):
        key = list(parse_item)[0]
        return {"AND": get_files_from_and, "OR": get_files_from_or}[key](parse_item[key])
    if isinstance(parse_item, str):
        return index_dict.get(parse_item)
