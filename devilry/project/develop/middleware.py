from django.contrib import auth
from django.conf import settings


class FakeLoginMiddleware(object):
    """
    Login using ?fakeuser=USERNAME as long as settings.DEBUG is true.

    This is for DEVELOPMENT ONLY.
    """
    def process_request(self, request):
        if settings.DEBUG and 'fakeuser' in request.GET:
            username = request.GET['fakeuser']

            # If the user is already authenticated and that user is the user we are
            # getting passed in the headers, then the correct user is already
            # persisted in the session and we don't need to continue.
            if request.user.is_authenticated():
                if request.user.username == username:
                    return

            # We are seeing this user for the first time in this session, attempt
            # to authenticate the user.
            user = auth.authenticate(username=username, password='test')
            if user:
                # User is valid.  Set request.user and persist user in the session
                # by logging the user in.
                request.user = user
                auth.login(request, user)
