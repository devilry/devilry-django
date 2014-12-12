
#: The ISO datetime format without seconds on the format required by the ``date`` django template tag
DJANGO_ISODATETIMEFORMAT = 'Y-m-d H:i'


def isoformat_datetime(datetimeobj):
    return datetimeobj.strftime('%Y-%m-%d %H:%M')

