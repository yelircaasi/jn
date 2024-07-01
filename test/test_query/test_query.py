from jn.editing import wrapped_test_query


test_dict = {
    "ID0001": {
        "text": "",
        "link": "",
        "type": "",
        "subtype": "",
        "tags": [""],
        "subtags": [""],
        "status": "",
        "dateCreated": "",
        "dateModified": "",
        "extra": {"language": "", "progLang": ""},
        "sorter": "",
        "id": "",
    },
    "ID0002": {},
    "ID0003": {},
    "ID0004": {},
    "ID0005": {},
    "ID0006": {},
    "ID0007": {},
    "ID0008": {},
    "ID0009": {},
    "ID0010": {},
    "ID0011": {},
    "ID0012": {},
    "ID0013": {},
    "ID0014": {},
    "ID0015": {},
    "ID0016": {},
    "ID0017": {},
    "ID0018": {},
    "ID0019": {},
    "ID0020": {},
    "ID0021": {},
    "ID0022": {},
    "ID0023": {},
    "ID0024": {},
    "ID0025": {},
    "ID0026": {},
    "ID0027": {},
    "ID0028": {},
    "ID0029": {},
    "ID0030": {},
    "ID0031": {},
    "ID0032": {},
}


def parse_and_output_all(query: str) -> tuple:
    ...


case_and_single           = "a.b"                               # ✔
case_and                  = "ab.cd"                             # ✔
case_or_single            = "a.b"                               # ✔
case_or                   = "ab.cd"                             # ✔
case_precedence           = "tagName1.tagName2,tagName3"        # ✔
case_simple_noval         = "+extraTag1"                        # ✔
case_simple_extra         = "+extraTag1:extraTagValue"          # ✔
case_simple_status        = "/statusName1"                      # ✔
case_simple_rating        = "*3.3"                              # ✔
case_simple_tag           = "tagName"                           # ✔
case_simple_tag_subtag    = "tagName1:subtagName1"              # ✔
case_simple_embeddedregex = "〈[rR]eg.x\d,\d[[2,4]]-[A-Z]+\s?〉"   # ✔ 
case_simple_textregex     = "⸨[rR]eg.x\d,\d[[2,4]]-[A-Z]+\s?⸩"  # ✔ 
case_simple_fullregex     = "⦃[rR]eg.x\d,\d[[2,4]]-[A-Z]+\s?⦄"  # ✔ 
case_simple_linkregex     = "«[rR]eg.x\d,\d[[2,4]]-[A-Z]+\s?»"  # ✔ 
case_simple_type_subtype  = "%typeName:subtypeName"             # ✔
case_simple_type          = "%typeName"                         # ✔
case_simple_date_created  = "©2022-03-15"                       # ✔
case_simple_date_modified = "^2024-06-17"                       # ✔
case_simple_proglang      = "❱haskell"                          # ✔
case_simple_language      = "€EN"                               # ✔

case_and_single_neg           = "~a.~b"
case_and_neg                  = "~ab.~cd"
case_or_single_neg            = "~a.~b"
case_or_neg                   = "~ab.~cd"
case_precedence_neg           = "~tag1.~tag2,~tag3"
case_simple_extra_neg         = "+~extraTag1"
case_simple_status_neg        = "/~status1"
case_simple_rating_neg        = "*~4"
case_simple_tag_neg           = "~tagName1"
case_simple_tag_subtag_neg    = "tagName1:~subtagName"
case_simple_embeddedregex_neg = "~〈someRegex〉"
case_simple_textregex_neg     = "~⸨someRegex⸩"
case_simple_fullregex_neg     = "~⟪someRegex⟫"
case_simple_type_subtype_neg  = "%typeName:~subtypeName"
case_simple_type_neg          = "%~typeName"
case_simple_date_created_neg  = "©~2022-03-15"
case_simple_date_modified_neg = "^~2024-06-17"
case_simple_proglang_neg      = "❱~haskell"
case_simple_language_neg      = "€~EN"

case_simple_rating_exact        = "*~~4.0"         # ✔
case_simple_date_created_exact  = "©~~2019-04-06"  # ✔
case_simple_date_modified_exact = "^~~2021-07-10"  # ✔

case_and_single_opt           = "a?.b?"
case_and_opt                  = "ab?.cd?"
case_or_single_opt            = "?a,?b"
case_or_opt                   = "ab?.cd?"
case_or_opt                   = "ab?.cd?"
case_precedence_opt           = "tag1?.tag2?,tag3?"
case_simple_extra_opt         = "+?extraTagName:extraTagValue"
case_simple_status_opt        = "/?status"
case_simple_rating_opt        = "*?4.1"
case_simple_tag_opt           = "?tagString"
case_simple_tag_subtag_opt    = "tagString:?subtagString"
case_simple_embeddedregex_opt = "?〈someRegex〉"
case_simple_textregex_opt     = "?⸨someRegex⸩"
case_simple_fullregex_opt     = "?⟪someRegex⟫"
case_simple_type_subtype_opt  = "typeName:?subtypeName"
case_simple_type_opt          = "%?typeName"
# case_simple_date_created_opt = "©?"
# case_simple_date_modified_opt = ""
case_simple_proglang_opt = "❱?python"
case_simple_language_opt = "€?EN"

case_and_single_neg_opt           = "?~a.?~b"
case_and_neg_opt                  = "?~ab.cd"
case_or_single_neg_opt            = "?~a.?~b"
case_or_neg_opt                   = "?~ab.cd"
case_precedence_neg_opt           = "tag1.?~,tag3"
case_simple_extra_neg_opt         = "?~extraName:extraValue"
case_simple_status_neg_opt        = "/?~statusName"
case_simple_rating_neg_opt        = "*?~3.0"
case_simple_tag_neg_opt           = "?~tagName"
case_simple_tag_subtag_neg_opt    = "tagName:?~subtagName"
case_simple_embeddedregex_neg_opt = "?~〈someRegex〉"
case_simple_textregex_neg_opt     = "?~⸨someRegex⸩"
case_simple_fullregex_neg_opt     = "?~⟪someRegex⟫"
case_simple_type_subtype_neg_opt  = "%typeName:?~subtypeName"
case_simple_type_neg_opt          = "%?~typeName"
case_simple_date_created_neg_opt  = "©?~2025-12-31"
case_simple_date_modified_neg_opt = "^?~2030-04-05"
case_simple_proglang_neg_opt      = "❱?~python"
case_simple_language_neg_opt      = "€?~EN"

# need to tokenize this as EXACT_NOT
case_simple_rating_neg_exact        = "*~~~3.0"         # can easily do wthout this
case_simple_date_created_neg_exact  = "©~~~2023-05-31"  # really necessary?
case_simple_date_modified_neg_exact = "^~~~2024-11-21"  # really necessary?

case_simple_rating_neg_exact_opt        = "?~~~4.5"
case_simple_date_created_neg_exact_opt  = "©?~~~2022-10-13"
case_simple_date_modified_neg_exact_opt = "?~~~2020-05-18"


regex_special = [
    "[",
    "]",
    "{",
    "}",
    "-",
    "\\",
    "(",
    ")",
    "*",
    "^",
    "$",
    "=",
    ""
]