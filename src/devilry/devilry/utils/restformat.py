def format_datetime(datetime):
    return datetime.strftime('%Y-%m-%d %H:%M:%S')

def format_timedelta(timedelta_obj):
    hours, remainder = divmod(timedelta_obj.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if timedelta_obj.days >= 0:
        days = timedelta_obj.days
    else:
        days = abs(timedelta_obj.days) - 1
    return {'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds}
