from django.conf import settings


def should_skip_tests_that_require_rq_async():
    if settings.DEVILRY_SKIP_RQ_TESTS:
        return True
    return False
