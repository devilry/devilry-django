from functools import wraps
from django.http import HttpResponseForbidden


def forbidden_if_not_authenticated(f):
    """ Very similar to :func:`django.contrib.auth.decorators.login_required`,
    however it returns class:`django.http.HttpResponseForbidden` instead of
    redirecting to login. """
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated():
            return f(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()
    return wrapper
