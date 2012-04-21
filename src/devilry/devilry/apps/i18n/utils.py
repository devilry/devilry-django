import re
from django.utils.translation.trans_real import parse_accept_lang_header
from django.conf import settings

def get_languagecode_from_httpheader(accept_language_header, languagemapping):
    for languagecode , priority in parse_accept_lang_header(accept_language_header): # NOTE: parse_accept_lang_header returns accept_lang sorted by priority
        if languagecode == '*':
            break
        if languagecode in languagemapping:
            return languagecode
    return None


def get_languagecode(user, accept_language_header=None,
                     languagecodemapping=settings.DEVILRY_I18N_LANGCODEMAPPING,
                     default_languagecode=settings.DEVILRY_I18N_DEFAULT_LANGCODE):
    """
    Get the appropriate language code from the provided information:

    1. If the user has a valid languagecode in their preferences, use it.
    2. Check the ACCEPT_LANGUAGE HTTP header, and use it as long as parsing it yields a
       language code that is is ``languagecodemapping``.
    3. Return the default_languagecode as the last fallback.

    As long as ``default_languagecode`` is in ``languagecodemapping``, this function
    is guaranteed to yield a language code that is present as a key in
    ``languagecodemapping``.
    """
    if user.is_authenticated():
        languagecode = user.get_profile().languagecode
        if languagecode and languagecode in languagecodemapping:
            return languagecode

    if accept_language_header:
        languagecode = get_languagecode_from_httpheader(accept_language_header, languagecodemapping)
        if languagecode:
            return languagecode

    return default_languagecode


find_all_translatestrings_patt = re.compile(r"""dtranslate\(['"]([a-z._-]+)['"]\)""")
def find_all_translatestrings(data):
    return find_all_translatestrings_patt.findall(data)
