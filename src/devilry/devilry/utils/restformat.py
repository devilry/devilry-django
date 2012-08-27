def format_datetime(datetime):
    return datetime.strftime('%Y-%m-%d %H:%M:%S')

def format_timedelta(timedelta_obj):
    total_seconds = abs(timedelta_obj.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return {'days': int(days),
            'hours': int(hours),
            'minutes': int(minutes),
            'seconds': int(seconds)}
