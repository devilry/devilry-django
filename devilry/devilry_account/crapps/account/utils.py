import pycountry


def get_language_name(languagecode):
    out = None
    if len(languagecode) == 2:
        out = pycountry.languages.get(alpha_2=languagecode)
    elif len(languagecode) == 3:
        out = pycountry.languages.get(alpha_3=languagecode)
    if out:
        return out.name
    else:
        return languagecode
