from datetime import datetime, timedelta


def isoformat_datetime(datetimeobj):
    return datetimeobj.strftime('%Y-%m-%d %H:%M:%S')

def isoformat_relativetime(days):
    now = datetime.now()
    if days < 0:
        dt = now - timedelta(days=days)
    else:
        dt = now + timedelta(days=days)
    return isoformat_datetime(dt)
