from django.utils.translation.trans_real import parse_accept_lang_header


def get_languagecode(accept_language_header, languagemapping):
    for languagecode , priority in parse_accept_lang_header(accept_language_header): # NOTE: parse_accept_lang_header returns accept_lang sorted by priority
        if languagecode == '*':
            break
        if languagecode in languagemapping:
            return languagecode
    return None
