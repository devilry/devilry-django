from django.contrib.auth.decorators import login_required
from django.contrib import auth

from xmlrpc import XmlRpc


USER_DISABLED = 1
SUCCESSFUL_LOGIN = 2
LOGIN_FAILED = 3
rpc = XmlRpc('login', 'devilry-xmlrpc-login')


@rpc.rpcdec()
def login(request, username, password):
    """ Authenticate with the django server and begin a HTTP cookie-based
    session. """
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            return SUCCESSFUL_LOGIN
        else:
            return USER_DISABLED
    else:
        return LOGIN_FAILED


@rpc.rpcdec()
@login_required
def logout(request):
    """ End a active session. """
    auth.logout(request)


@rpc.rpcdec()
@login_required
def sum(request, a, b):
    """ A simple function used only for debugging and testing.

    :return: The sum of *a* and *b* in a string with some extra information.
    """
    return "Hello %s. %d+%d == %d" % (request.user, a, b, a + b)
