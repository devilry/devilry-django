import datetime
from django.utils import timezone


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
    return timezone.make_aware(
        datetime.datetime(*args, **kwargs),
        timezone.get_default_timezone())
