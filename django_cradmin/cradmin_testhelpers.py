import json

import htmls
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from unittest import mock
from model_bakery import baker


def _indent_string(string):
    try:
        return "\n".join(["   {}".format(line) for line in string.split("\n")])
    except:
        return string


class MockRequestResponse(object):
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


class AbstractTestCaseMixin(object):
    """
    Implements the common API for the test case mixins.
    """

    #: The view class - must be set in subclasses unless
    #: you override :meth:`~.AbstractTestCaseMixin.get_viewclass`.
    viewclass = None

    def get_viewclass(self):
        """
        Get the view class. Defaults to :obj:`.~AbstractTestCaseMixin.viewclass`
        """
        return self.viewclass

    def make_view(self):
        """
        Make view function.

        Calls ``get_viewclass().as_view()`` by default.
        """
        viewclass = self.get_viewclass()
        if self.viewclass is None:
            raise NotImplementedError("You must set the viewclass attribute on TestCase classes using TestCaseMixin.")
        return viewclass.as_view()

    def get_requestfactory_class(self):
        """
        Get the request factory class.

        Must be implemented in subclasses.
        """
        raise NotImplementedError()

    def make_requestfactory(self):
        return self.get_requestfactory_class()()

    def create_default_user_for_mock_request(self):
        """
        Create default user for mock request.

        Defaults to returning ``baker.make(settings.AUTH_USER_MODEL)``,
        which should create a user no matter what user model you
        are using, unless you do something very complex for users.

        You can override this if you want to change the default
        properties of users for all tests in this testcase, but
        it is normally better to just use the ``requestuser`` kwarg
        for :meth:`.mock_request` (or any of the more specialized
        ``mock_*request(..)`` methods)

        Must return a user object compatible with ``django.http.HttpRequest.user``.
        This means that the method can also return an AnonymousUser, but if you need this
        you should use :class:`.NoLoginTestCaseMixin` (which just overrides this method).
        """
        return baker.make(settings.AUTH_USER_MODEL)

    def make_minimal_request(self, method, requestkwargs=None, httpheaders=None):
        """
        Make a minimal request object.

        Args:
            method (str): The http method (get, post, ...).
            requestkwargs (dict): Kwargs for the request. Defaults to
                ``{'path': '/'}``, and the path is added unless it is
                included in the dict. The data you can include in this
                dict is the same as for the get, post, ... methods on
                :class:`.django.test.Client` (depends on the ``method`` kwarg).
            httpheaders (dict): Extra http headers needed.

        Returns:
            The created request object.
        """
        requestkwargs_full = {"path": "/"}
        if requestkwargs:
            requestkwargs_full.update(requestkwargs)
        if httpheaders:
            requestkwargs_full.update(httpheaders)
        request = getattr(self.make_requestfactory(), method)(**requestkwargs_full)
        return request

    def add_essential_cradmin_attributes_to_request(
        self, request, requestuser, cradmin_role, cradmin_app, cradmin_instance, sessionmock, messagesmock
    ):
        request.user = requestuser or self.create_default_user_for_mock_request()
        request.cradmin_role = cradmin_role or mock.MagicMock()
        request.cradmin_app = cradmin_app or mock.MagicMock()
        request.cradmin_instance = cradmin_instance or mock.MagicMock()
        request.session = sessionmock or mock.MagicMock()
        request._messages = messagesmock or mock.MagicMock()
        return request

    def __add_selector_to_mockresponse(self, mockresponse):
        mockresponse.response.render()
        mockresponse.selector = htmls.S(mockresponse.response.content)

    def prettyformat_response_content(self, response):
        """
        Must be implemented in subclasses.
        """
        raise NotImplementedError()

    def prettyformat_response_meta(self, response):
        return ("status_code={status_code}\ncharset={charset}\nreason_phrase={reason_phrase}").format(
            status_code=response.status_code,
            charset=response.charset,
            reason_phrase=response.reason_phrase,
        )

    def prettyformat_response(self, response):
        meta = self.prettyformat_response_meta(response)
        content, warnings = self.prettyformat_response_content(response)
        return "[cradmin TestCaseMixin info]: HttpRequest meta:\n{meta}\n{warnings}\n{content}".format(
            meta=_indent_string(meta), warnings="\n".join(warnings), content=content
        )

    def assert_status_code_of_response(self, response, expected_statuscode):
        errormessage = "Expected HTTP response with status code {expected}. Got {actual}.".format(
            expected=expected_statuscode, actual=response.status_code
        )
        self.assertEqual(response.status_code, expected_statuscode, msg=errormessage)

    def mock_request(
        self,
        method,
        cradmin_role=None,
        cradmin_app=None,
        cradmin_instance=None,
        requestuser=None,
        messagesmock=None,
        sessionmock=None,
        requestattributes=None,
        httpheaders=None,
        requestkwargs=None,
        viewkwargs=None,
        expected_statuscode=None,
        htmls_selector=False,
        verbose=False,
    ):
        """
        Create a mocked request using :meth:`.make_requestfactory` and :class:`mock.MagicMock`.

        Parameters:
            method: The http method (get, post, ...).
            httpheaders (httpheaders): Forwarded to :meth:`.make_minimal_request`.
                Extra HTTP headers to be added to request.META.
            requestkwargs (dict): Forwarded to :meth:`.make_minimal_request`.

            cradmin_role: The request.cradmin_role to use. Defaults to mock.MagicMock().
            cradmin_app: The request.cradmin_app to use. Defaults to mock.MagicMock().
            cradmin_instance: The request.cradmin_instance to use. Defaults to mock.MagicMock().
            requestuser: The request.requestuser to use. Defaults to mock.MagicMock().
            sessionmock: The request.session to use. Defaults to mock.MagicMock().
            messagesmock: The request._messages to use. Defaults to mock.MagicMock().

            requestattributes (dict): Extra attributes to the reques to object.
                This is applied before :meth:`.add_essential_cradmin_attributes_to_request`,
                so any of the attributes that method sets can not be in this dics.
            viewkwargs (dict): Kwargs for the view.
            expected_statuscode (int): Expected status code. If this is ``None``,
                we do not validate the status code. Defaults to ``None``.
            htmls_selector (boolean): If this is ``True``, we create a ``htmls.S()``
                object for the response content. Should normally not be used without
                also providing ``expected_statuscode`` because it can lead to
                unexpected behavior. Defaults to ``False``.
            verbose (boolean): More verbose exception messages. Useful for debugging,
                but should be ``False`` when you are not debugging. Defaults
                to ``False``.
        """
        request = self.make_minimal_request(method=method, requestkwargs=requestkwargs, httpheaders=httpheaders)
        if requestattributes:
            for key, value in requestattributes.items():
                setattr(request, key, value)
        self.add_essential_cradmin_attributes_to_request(
            request=request,
            requestuser=requestuser,
            cradmin_role=cradmin_role,
            cradmin_app=cradmin_app,
            cradmin_instance=cradmin_instance,
            sessionmock=sessionmock,
            messagesmock=messagesmock,
        )
        viewkwargs = viewkwargs or {}
        response = self.make_view()(request, **viewkwargs)

        if verbose:
            print(self.prettyformat_response(response=response))

        if expected_statuscode is not None:
            self.assert_status_code_of_response(response=response, expected_statuscode=expected_statuscode)
        mockresponse = MockRequestResponse(response=response, request=request)
        if htmls_selector:
            self.__add_selector_to_mockresponse(mockresponse)
        return mockresponse

    def mock_getrequest(self, **kwargs):
        return self.mock_request(method="get", **kwargs)

    def mock_http302_getrequest(self, **kwargs):
        kwargs["expected_statuscode"] = 302
        return self.mock_getrequest(**kwargs)

    def mock_postrequest(self, **kwargs):
        return self.mock_request(method="post", **kwargs)

    def mock_http302_postrequest(self, **kwargs):
        kwargs["expected_statuscode"] = 302
        return self.mock_postrequest(**kwargs)

    def mock_http200_postrequest(self, **kwargs):
        kwargs["expected_statuscode"] = 200
        return self.mock_postrequest(**kwargs)

    def mock_http201_postrequest(self, **kwargs):
        kwargs["expected_statuscode"] = 201
        return self.mock_postrequest(**kwargs)

    def mock_http400_postrequest(self, **kwargs):
        kwargs["expected_statuscode"] = 400
        return self.mock_postrequest(**kwargs)

    def mock_http403_postrequest(self, **kwargs):
        kwargs["expected_statuscode"] = 403
        return self.mock_postrequest(**kwargs)

    def mock_putrequest(self, **kwargs):
        return self.mock_request(method="put", **kwargs)

    def mock_patchrequest(self, **kwargs):
        return self.mock_request(method="patch", **kwargs)

    def mock_deleterequest(self, **kwargs):
        return self.mock_request(method="delete", **kwargs)


class TestCaseMixin(AbstractTestCaseMixin):
    """
    A mixin class that makes it easier to write tests for cradmin views.

    It mocks all the required attributes of the request object.

    Examples:

        Minimalistic::

            from django_cradmin import cradmin_testhelpers

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

        Adding optional HTTP headers if needed::

            from django_cradmin import cradmin_testhelpers

            class TestMyView(TestCase, cradmin_testhelpers.TestCaseMixin):
                viewclass = MyView

                def test_post_with_optional_httpheaders(self):
                    self.mock_postrequest(
                        cradmin_instance=cradmin_instance,
                        httpheaders={
                            'HTTP_REFERER': 'http://www.http-referent.com'
                        },
                        requestkwargs={
                            'data': {
                                'name': 'Jane Doe',
                                'age': 24
                            }
                        })
                    self.assertEqual(mockresponse.response.status_code, 302)

        Customizing the request.body, if e.g you have created a view that works as an API that handles POST with
        data. This data will in most cases be JSON. If this is not done through a form, but javascript,
        the data will end up in request.body, and not request.POST. To have this functionality when testing,
        simply add the data you want to _body in requestattributes. request._body is the actual attribute, and
        request.body is a property::

            from django_cradmin import cradmin_testhelpers

            class TestMyView(TestCase, cradmin_testhelpers.TestCaseMixin):
                viewclass = MyView

                def test_post_with_optional_httpheaders(self):
                    self.mock_postrequest(
                        cradmin_instance=cradmin_instance,
                        requestattributes={
                            '_body': b'{'key': 'value'}'
                        })
                    self.assertEqual(mockresponse.response.status_code, 302)

        Views that take arguments::

            from django_cradmin import cradmin_testhelpers

            class TestMyView(TestCase, cradmin_testhelpers.TestCaseMixin):
                viewclass = MyView

                def test_get_render_form(self):
                    # The kwargs for mock_postrequest, mock_http200_getrequest_htmls
                    # and mock_getrequest are the same, so only showing one for brevity.
                    mockresponse = self.mock_http200_getrequest_htmls(viewkwargs={'pk': 10})

        Views that use a querystring (GET)::

            from django_cradmin import cradmin_testhelpers

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

            from django_cradmin import cradmin_testhelpers

            class TestMyView(TestCase, cradmin_testhelpers.TestCaseMixin):
                viewclass = MyView

                def test_post(self):
                    requestuser = baker.make(settings.AUTH_USER_MODEL)
                    mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)

        Mocking Django messages framework messages::

            from django_cradmin import cradmin_testhelpers

            class TestMyView(TestCase, cradmin_testhelpers.TestCaseMixin):
                viewclass = MyView

                def test_post(self):
                    messagesmock = mock.MagicMock()
                    mockresponse = self.mock_postrequest(
                        requestkwargs={
                            'data': {
                                'name': 'Jane Doe',
                                'age': 24
                        },
                        messagesmock=messagesmock
                    )
                    messagesmock.add.assert_called_once_with(
                        messages.SUCCESS,
                        'The data was posted successfully!',
                        '')

        Get a bit of extra information useful while debugging
        failing tests - use ``verbose=True`` (only for debugging, do
        not keep/commit verbose=True)::

            from django_cradmin import cradmin_testhelpers

            class TestMyView(TestCase, cradmin_testhelpers.TestCaseMixin):
                viewclass = MyView

                def test_get(self):
                    mockresponse = self.mock_http200_getrequest_htmls(
                        verbose=True
                    )

    """

    def get_requestfactory_class(self):
        """
        Get the request factory class. Defaults to :class:`django.test.RequestFactory`.
        """
        return RequestFactory

    def prettyformat_response_content(self, response):
        warnings = []
        output = None
        if hasattr(response, "render"):
            try:
                response.render()
            except Exception as e:
                warnings.append("[cradmin TestCaseMixin warning] response.render() failed with: {}".format(e))
            else:
                try:
                    output = "[cradmin TestCaseMixin info]: Prettyformatted response.content:\n{}".format(
                        _indent_string(htmls.S(response.content).prettify())
                    )
                except:
                    pass
        if output is None:
            try:
                content = response.content.decode("utf-8")
            except UnicodeError:
                content = response.content
            if content:
                output = "[cradmin TestCaseMixin info]: response.content:\n{}".format(_indent_string(content))
            else:
                output = "[cradmin TestCaseMixin info]: response.content is empty."
        return output, warnings

    def mock_http200_getrequest_htmls(self, **kwargs):
        kwargs["expected_statuscode"] = 200
        kwargs["htmls_selector"] = True
        return self.mock_getrequest(**kwargs)

    def mock_http200_postrequest_htmls(self, **kwargs):
        kwargs["expected_statuscode"] = 200
        kwargs["htmls_selector"] = True
        return self.mock_postrequest(**kwargs)


class NoLoginTestCaseMixin(TestCaseMixin):
    """
    Use this instead of :class:`.TestCaseMixin` if you do not require
    an authenticated user in your view.
    """

    def create_default_user_for_mock_request(self):
        """
        Overridden to return a :class:`django.contrib.auth.models.AnonymousUser`
        object instead of creating a user.
        """
        return AnonymousUser()


class RestFrameworkApiTestCaseMixin(TestCaseMixin):
    """
    Django-rest-framework API test case mixin.

    Works just like :class:`.TestCaseMixin`, except that it
    has a different debug output, and no ``*_htmls`` methods.

    Assumes that the viewclass is a subclass of :class:`rest_framework.views.APIView`.

    You can also make it work with viewsets by overriding :meth:`~.AbstractTestCaseMixin.make_view`
    and use ``return ViewSetClass.as_view({...})`` there.
    """

    def get_requestfactory_class(self):
        # Importing it here to avoid har dependency on rest framework.
        from rest_framework.test import APIRequestFactory

        return APIRequestFactory

    def prettyformat_response_content(self, response):
        warnings = []
        output = None
        if hasattr(response, "data"):
            output = _indent_string(json.dumps(response.data, indent=4))
        else:
            warnings.append("[cradmin RestFrameworkApiTestCaseMixin warning] Response has no data attribute.")
        if output is None:
            try:
                content = response.content.decode("utf-8")
            except UnicodeError:
                content = response.content
            if content:
                output = "[cradmin RestFrameworkApiTestCaseMixin info]: response.content:\n{}".format(
                    _indent_string(content)
                )
            else:
                output = "[cradmin RestFrameworkApiTestCaseMixin info]: response.content is empty."
        return output, warnings

    def mock_request(self, **kwargs):
        requestkwargs = kwargs.pop("requestkwargs", {})
        requestkwargs["format"] = requestkwargs.get("format", "json")
        kwargs["requestkwargs"] = requestkwargs
        return super(RestFrameworkApiTestCaseMixin, self).mock_request(**kwargs)
