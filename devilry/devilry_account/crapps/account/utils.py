import pycountry


def get_language_name(languagecode):
    try:
        if len(languagecode) == 2:
            return pycountry.languages.get(alpha_2=languagecode).name
        elif len(languagecode) == 3:
            return pycountry.languages.get(alpha_3=languagecode).name
        return languagecode
    except Exception:
        return languagecode