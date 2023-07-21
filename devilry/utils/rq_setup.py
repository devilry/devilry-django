def make_rq_queue_queue_setting(host='localhost', port=6379, db=0, password=None, default_timeout=500):
    config = {
        'HOST': host,
        'PORT': port,
        'DB': db,
        'DEFAULT_TIMEOUT': default_timeout
    }
    if password:
        config.update({'PASSWORD': password})
    return config


def make_simple_rq_queue_setting(host='localhost', port=36314, db=0, password=None, default_timeout=500):
    return {
        'default': make_rq_queue_queue_setting(
            host=host,
            port=port,
            db=db,
            password=password,
            default_timeout=default_timeout),
        'email': make_rq_queue_queue_setting(
            host=host,
            port=port,
            db=db,
            password=password,
            default_timeout=default_timeout),
        'highpriority': make_rq_queue_queue_setting(
            host=host,
            port=port,
            db=db,
            password=password,
            default_timeout=default_timeout),
    }
