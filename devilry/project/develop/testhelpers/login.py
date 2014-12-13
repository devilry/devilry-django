class LoginTestCaseMixin(object):
    """
    Mixin class for TestCase that makes it easy to test views as an authenticated user.

    Example::

        from django.test import TestCase
        from develop.testhelpers.login import LoginTestCaseMixin
        from develop.testhelpers.corebuilder import UserBuilder

        class TestSomeView(TestCase, LoginTestCaseMixin):

            def test_something(self):
                someuser = UserBuilder('someuser').user
                response = self.get_as(someuser, '/some/url')

    """
    def login(self, user, password='test'):
        """
        Login the given ``user``.
        """
        self.client.login(username=user.username, password=password)

    def get_as(self, user, *args, **kwargs):
        """
        """
        self.login(user)
        return self.client.get(*args, **kwargs)

    def post_as(self, user, *args, **kwargs):
        """
        Just like ``client.post(...)``, except that the first argument is
        the user you want to login as before performing the GET request.
        """
        self.login(user)
        return self.client.post(*args, **kwargs)
