import datetime

from django.utils import timezone


def make_aware_in_default_timezone(native_datetime_object):
    if timezone.is_aware(native_datetime_object):
        return native_datetime_object
    else:
        return timezone.make_aware(native_datetime_object, timezone.get_default_timezone())


def default_timezone_datetime(*args, **kwargs):
    """
    Create a timezone-aware ``datetime.datetime`` object.

    The parameters are the same as for ``datetime.datetime``.
    """
    return make_aware_in_default_timezone(datetime.datetime(*args, **kwargs))


def simplified_isoformat_datetime(datetime_object):
    return datetime_object.strftime("%Y-%m-%d %H:%M")


def now_simplified_isoformat():
    return simplified_isoformat_datetime(timezone.now())
