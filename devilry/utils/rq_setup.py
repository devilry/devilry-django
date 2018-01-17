def get_default_queue_setup_dict():
    """
    Override this to customize settings for default RQ-queue.
    """
    return {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 500
    }


def get_email_queue_setup_dict():
    """
    Override this to customize settings for email RQ-queue.
    """
    return {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 500
    }


def get_highpriority_queue_setup_dict():
    """
    Override this to customize settings for highpriority RQ-queue.
    """
    return {
        # 'URL': os.getenv('REDISTOGO_URL', 'redis://localhost:6379/0'),  # If you're on Heroku
        'HOST': 'redis://localhost:6379/0',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 500
    }
