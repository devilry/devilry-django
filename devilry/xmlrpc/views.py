from django.contrib import auth

from xmlrpc import XmlRpc


USER_DISABLED = 1
LOGIN_FAILED = 2
SUCCESSFUL_LOGIN = 3
rpc = XmlRpc('login', 'devilry-xmlrpc-login')


@rpc.rpcdec('username, password')
def login(request, username, password):
    """ Authenticate with the django server and begin a HTTP cookie-based
    session.
    
    :return: *1* if the user is disabled, *2* if login failed and *3*
             on successful login.
    """
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            return SUCCESSFUL_LOGIN
        else:
            return USER_DISABLED
    else:
        return LOGIN_FAILED

@rpc.rpcdec_login_required()
def logout(request):
    """ End a active session. """
    auth.logout(request)

@rpc.rpcdec_login_required('a, b')
def sum(request, a, b):
    """ A simple function used only for debugging and testing.

    :return: The sum of *a* and *b* in a string with some extra information.
    """
    return "Hello %s. %d+%d == %d" % (request.user, a, b, a + b)
