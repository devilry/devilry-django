from django.conf import settings
from django.test import RequestFactory
import htmls
from model_bakery import baker

from unittest import mock


class MockRequestResponse:
    """
    Return type of :meth:`.TestCaseMixin.mock_request`,
    :meth:`.TestCaseMixin.mock_http200_getrequest_htmls` and
    :meth:`.TestCaseMixin.mock_postrequest`.

    .. attribute:: response

        The HttpResponse object.

    .. attribute:: request

        The RequestFactory-generated HttpRequest object.

    .. attribute:: selector

        A ``htmls.S`` object created with the entire content of the
        response as input. Only available when using
        :meth:`.TestCaseMixin.mock_http200_getrequest_htmls`.
    """

    def __init__(self, response, request):
        self.response = response
        self.request = request
        self.selector = None


class TestCaseMixin:
    """
    A mixin class that makes it easier to write tests for cradmin views.

    It mocks all the required attributes of the request object.

    Examples:

        Minimalistic::

            from cradmin_legacy import cradmin_testhelpers

            class TestMyView(TestCase, cradmin_testhelpers.TestCaseMixin):
                viewclass = MyView

                def test_get_render_form(self):
                    mockresponse = self.mock_http200_getrequest_htmls()
                    mockresponse.selector.prettyprint()

                def test_post(self):
                    mockresponse = self.mock_postrequest(requestkwargs={
                        'data': {
                            'name': 'Jane Doe',
                            'age': 24
                        }
                    })
                    self.assertEqual(mockresponse.response.status_code, 302)


        Views that take arguments::

            from cradmin_legacy import cradmin_testhelpers

            class TestMyView(TestCase, cradmin_testhelpers.TestCaseMixin):
                viewclass = MyView

                def test_get_render_form(self):
                    # The kwargs for mock_postrequest, mock_http200_getrequest_htmls
                    # and mock_getrequest are the same, so only showing one for brevity.
                    mockresponse = self.mock_http200_getrequest_htmls(viewkwargs={'pk': 10})

        Views that use a querystring (GET)::

            from cradmin_legacy import cradmin_testhelpers

            class TestMyView(TestCase, cradmin_testhelpers.TestCaseMixin):
                viewclass = MyView

                def test_get_render_form(self):
                    mockresponse = self.mock_http200_getrequest_htmls(
                        requestkwargs={
                            'data': {
                                'orderby': 'name'
                            }
                        }
                    )

        Using a real user object::

            from cradmin_legacy import cradmin_testhelpers

            class TestMyView(TestCase, cradmin_testhelpers.TestCaseMixin):
                viewclass = MyView

                def test_post(self):
                    requestuser = baker.make(settings.AUTH_USER_MODEL)
                    mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)

        Mocking Django messages framework messages::

            from cradmin_legacy import cradmin_testhelpers

            class TestMyView(TestCase, cradmin_testhelpers.TestCaseMixin):
                viewclass = MyView

                def test_post(self):
                    messagesmock = mock.MagicMock()
                    mockresponse = self.mock_postrequest(data={
                        'name': 'Jane Doe',
                        'age': 24
                    }, messagesmock=messagesmock)
                    messagesmock.add.assert_called_once_with(
                        messages.SUCCESS,
                        'The data was posted successfully!',
                        '')

    """

    #: The view class - must be set in subclasses
    viewclass = None

    def create_default_user_for_mock_request(self):
        return baker.make(settings.AUTH_USER_MODEL)

    def mock_request(
        self,
        method,
        cradmin_role=None,
        cradmin_app=None,
        cradmin_instance=None,
        requestuser=None,
        messagesmock=None,
        sessionmock=None,
        requestattributes={},
        requestkwargs=None,
        viewkwargs=None,
    ):
        """
        Create a mocked request using ``RequestFactory`` and ``mock.MagicMock``.

        Parameters:
            method: The http method (get, post, ...).
            cradmin_role: The request.cradmin_role to use. Defaults to mock.MagicMock().
            cradmin_app: The request.cradmin_app to use. Defaults to mock.MagicMock().
            cradmin_instance: The request.cradmin_instance to use. Defaults to mock.MagicMock().
            requestuser: The request.requestuser to use. Defaults to mock.MagicMock().
            sessionmock: The request.session to use. Defaults to mock.MagicMock().
            messagesmock: The request._messages to use. Defaults to mock.MagicMock().
        """
        if self.viewclass is None:
            raise NotImplementedError("You must set the viewclass attribute on TestCase classes using TestCaseMixin.")
        requestkwargs_full = {"path": "/"}
        if requestkwargs:
            requestkwargs_full.update(requestkwargs)
        viewkwargs = viewkwargs or {}
        request = getattr(RequestFactory(), method)(**requestkwargs_full)
        if requestattributes:
            for key, value in requestattributes.items():
                setattr(request, key, value)
        request.user = requestuser or self.create_default_user_for_mock_request()
        request.cradmin_role = cradmin_role or mock.MagicMock()
        request.cradmin_app = cradmin_app or mock.MagicMock()
        request.cradmin_instance = cradmin_instance or mock.MagicMock()
        request.session = sessionmock or mock.MagicMock()
        request._messages = messagesmock or mock.MagicMock()
        response = self.viewclass.as_view()(request, **viewkwargs)
        return MockRequestResponse(response=response, request=request)

    def mock_getrequest(self, **kwargs):
        return self.mock_request(method="get", **kwargs)

    def mock_http302_getrequest(self, **kwargs):
        mockresponse = self.mock_request(method="get", **kwargs)
        self.assertEqual(mockresponse.response.status_code, 302)
        return mockresponse

    def mock_http200_getrequest_htmls(self, **kwargs):
        mockresponse = self.mock_getrequest(**kwargs)
        self.assertEqual(mockresponse.response.status_code, 200)
        mockresponse.response.render()
        selector = htmls.S(mockresponse.response.content)
        mockresponse.selector = selector
        return mockresponse

    def mock_postrequest(self, **kwargs):
        return self.mock_request(method="post", **kwargs)

    def mock_http200_postrequest_htmls(self, **kwargs):
        mockresponse = self.mock_postrequest(**kwargs)
        self.assertEqual(mockresponse.response.status_code, 200)
        mockresponse.response.render()
        selector = htmls.S(mockresponse.response.content)
        mockresponse.selector = selector
        return mockresponse

    def mock_http302_postrequest(self, **kwargs):
        mockresponse = self.mock_postrequest(**kwargs)
        self.assertEqual(mockresponse.response.status_code, 302)
        return mockresponse
