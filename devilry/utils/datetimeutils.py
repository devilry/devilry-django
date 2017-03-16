import datetime
from django.conf import settings

from django.utils import timezone
#: Django datetime formatting string for ``YYYY-MM-DD hh:mm``.
ISODATETIME_DJANGOFORMAT = 'Y-m-d H:i'


def get_current_datetime():
    """
    Get the current datetime as a ``datetime.datetime`` object.

    We use this because it is easier to mock in unit tests than a built-in
    or third party implementation.
    """
    return timezone.now()


def default_timezone_datetime(*args, **kwargs):
    """
    Create a timezone-aware ``datetime.datetime`` object.

    The parameters are the same as for ``datetime.datetime``.
    """
    datetimeobject = datetime.datetime(*args, **kwargs)
    if settings.USE_TZ:
        return timezone.make_aware(
            datetimeobject,
            timezone.get_default_timezone())
    else:
        return datetimeobject


def isoformat_noseconds(datetimeobject):
    """
    Format the given ``datetime.datetime`` object as ``YYYY-MM-DD hh:mm``.
    """
    # We use isoformat because strftime does not support times before
    # year 1900.
    return datetimeobject.isoformat(' ').split('.')[0].rsplit(':', 1)[0]


def isoformat_withseconds(datetimeobject):
    """
    Format the given ``datetime.datetime`` object as ``YYYY-MM-DD hh:mm``.
    """
    # We use isoformat because strftime does not support times before
    # year 1900.
    return datetimeobject.isoformat(' ').split('.')[0]


def datetime_with_same_day_of_week_and_time(weekdayandtimesource_datetime, target_datetime):
    """
    Returns a new datetime object with the same time and day of week as
    the given ``target_datetime``, with the day of week moved forward
    to match the ``weekdayandtimesource_datetime``, and the time matching the
    ``weekdayandtimesource_datetime``.

    This means that if you send in a ``weekdayandtimesource_datetime`` with tuesday
    as the weekday, the return value will be a datetime object with the day set
    to the next tuesday unless the current day is monday or tuesday.
    """
    weekdayandtimesource_weekday = weekdayandtimesource_datetime.isoweekday()
    target_weekday = target_datetime.isoweekday()
    if weekdayandtimesource_weekday > target_weekday:
        added_days = weekdayandtimesource_weekday - target_weekday
    else:
        added_days = 7 - target_weekday + weekdayandtimesource_weekday
    new_datetimeobject = target_datetime + datetime.timedelta(days=added_days)
    new_datetimeobject = new_datetimeobject.replace(hour=weekdayandtimesource_datetime.hour,
                                                    minute=weekdayandtimesource_datetime.minute,
                                                    second=weekdayandtimesource_datetime.second,
                                                    microsecond=weekdayandtimesource_datetime.microsecond)
    return new_datetimeobject


def datetime_with_same_time(timesource_datetime, target_datetime):
    """
    Returns a new datetime object with the same day as the given ``target_datetime``,
    with the time replaced with the time from ``timesource_datetime``.
    """
    return target_datetime.replace(hour=timesource_datetime.hour,
                                   minute=timesource_datetime.minute,
                                   second=timesource_datetime.second,
                                   microsecond=timesource_datetime.microsecond)


URL_DATETIME_FORMAT = '%m_%d_%Y_%H_%M_%S'


def datetime_to_url_string(datetime_obj):
    """
    Converts datetime object to URL-friendly string.

    Args:
        datetime_obj (``django.utils.timezone``): ``datetime`` obj to convert.

    Returns:
        (str): Datetime as string specified by :attr:`.URL_DATETIME_FORMAT`.
    """
    return datetime_obj.strftime(URL_DATETIME_FORMAT)


def datetime_url_string_to_datetime(datetime_string):
    """
    Convert URL-friendly string to ``django.utils.timezone`` datetime object.
    Args:
        datetime_string (str): String to convert.

    Returns:
        (``django.utils.timezone``): Converted datetime object from string.
    """
    return timezone.datetime.strptime(datetime_string, URL_DATETIME_FORMAT)
