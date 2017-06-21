from datetime import datetime
from datetime import timedelta

DJANGO_ISODATETIMEFORMAT = 'Y-m-d H:i'


def isoformat_datetime(datetimeobj):
    return datetimeobj.strftime('%Y-%m-%d %H:%M')


class DateTimeBuilder(datetime):
    """
    Extends the builtin python :class:`datetime.datetime` with extra utility methods.

    Examples::

        tomorrow = DateTimeBuilder.now().plus(days=1)
        yesterday_startofday = DateTimeBuilder.now().daystart().minus(days=1)
    """
    def minus(self, weeks=0, days=0, hours=0, minutes=0, seconds=0):
        self -= timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds)
        return self

    def plus(self, weeks=0, days=0, hours=0, minutes=0, seconds=0):
        self += timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds)
        return self

    def daystart(self):
        """
        Set the time to ``00:00:00``.
        """
        self.replace(hour=0, minute=0, second=0, microsecond=0)
        return self

    def dayend(self):
        """
        Set the time to ``23:59:59``.
        """
        self.replace(hour=23, minute=59, second=59, microsecond=0)
        return self
