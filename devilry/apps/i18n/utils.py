from django.utils.translation.trans_real import parse_accept_lang_header
from django.conf import settings


def get_languagecode_from_httpheader(accept_language_header, languagemapping):
    for languagecode , priority in parse_accept_lang_header(accept_language_header): # NOTE: parse_accept_lang_header returns accept_lang sorted by priority
        if languagecode == '*':
            break
        if languagecode in languagemapping:
            return languagecode
    return None


def get_languagecode(request):
    if request.user.is_authenticated():
        languagecode = request.user.get_profile().languagecode
        if languagecode and languagecode in settings.DEVILRY_I18N_LANGCODEMAPPING:
            return languagecode

    if not languagecode:
        accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        if accept:
            languagecode = get_languagecode_from_httpheader(accept, settings.DEVILRY_I18N_LANGCODEMAPPING)
            if languagecode:
                return languagecode

    if not languagecode:
        return settings.DEVILRY_I18N_DEFAULT_LANGCODE
