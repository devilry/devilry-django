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

def serialize_user(user):
    return {'id': user.id,
            'username': user.username,
            'email': user.email,
            'displayname': user.fullname or user.username,
            'full_name': user.fullname}
