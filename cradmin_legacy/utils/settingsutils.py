from django.conf import settings


def cradmin_legacy_djangoadmin_user_search_fields(lookup: str = "user__") -> list[str]:
    search_fields = getattr(settings, "CRADMIN_LEGACY_DJANGOADMIN_USER_SEARCH_FIELDS", None) or []
    result = []
    for field in search_fields:
        prefix = ""
        if field[0] in ("=", "^", "@"):
            prefix = field[0]
            field = field[1:]
        result.append(f"{prefix}{lookup}{field}")
    return result
