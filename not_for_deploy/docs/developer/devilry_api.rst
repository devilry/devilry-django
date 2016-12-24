##########################################
:mod:`devilry_api` --- Devilry RESTFUL API
##########################################

.. module:: devilry_api

The ``devilry_api`` module is a RESTFUL api for devilry.


*****************
About devilry api
*****************
The devilry_api is built on django rest framework and documented with swagger.
For api documentation we use swagger, see /api/docs.


******************
What is an APIKey?
******************
The :class:`~devilry_api.APIKey` has a foreign key to a :class:`devilry_account.User` and stores information of its purpose and permission level.
It also has a key type which tells how long a key last from it's created datetime.
There are three types of permission classes, admin-, examiner- and student permission.
Each permission class has 3 types of permission levels, no permission which is the default, read only and write.

.. _devilry_api-how-to:

********************
How to create an api
********************
The following example will be for a student api, examiner and admin api's can be created similarly.
This guide will only cover how to create views and test them.
How to create a serializer see: http://www.django-rest-framework.org/api-guide/serializers/

Create the view
===============

Create a view inside something like ``devilry_api/my_api/views/my_view.py``::

    from rest_framework.generics import mixins, GenericAPIView
    from rest_framework.filters import OrderingFilter
    from devilry.devilry_api.auth.authentication import TokenAuthentication
    from devilry.devilry_api.my_api.serializers.serializer_student import MyStudentSerializer
    from devilry.devilry_api.permission.student_permission import StudentPermissionAPIKey
    from devilry.devilry_api.models import APIKey

    class MyView(mixins.ListModelMixin, GenericAPIView):
        serializer_class = MyStudentSerializer
        authentication_classes = (TokenAuthentication, )
        filter_backends = [OrderingFilter, ]

        #: student permission
        permission_classes = (StudentPermissionAPIKey, )

        #: We'll only allow read permission for this api
        api_key_permissions = (APIKey.STUDENT_PERMISSION_READ, )

        def get_queryset(self):
            """
            Return queryset for your model.
            """
            ...

        def get(self, request, *args, **kwargs):
            """
            List my model

            ---
            parameters:
                - name: ordering
                  required: false
                  paramType: query
                  type: String
                  description: ordering field
            """
            return super(MyView, self).list(request, *args, **kwargs)


Test the view
=============
`
For making testing easy we have created some useful mixins.

    :class:`devilry.devilry_api.tests.mixins.api_test_helper.TestCaseMixin`

        Used to create a request and returns a response.

    :class:`devilry.devilry_api.tests.mixins.test_common_mixins.TestAuthAPIKeyMixin`

        Tests the api key authentication for expired key's with different lifetimes. If we want to use this mixin,
        we have to create a ``get_apikey`` function

    :class:`devilry.devilry_api.tests.mixins.test_common_mixins.TestReadOnlyPermissionMixin`

        Test that a read only key does not have permission to perform write actions. If we want to use this mixin,
        we have to create a ``get_apikey`` function or we can inherit it along with the next following mixins.

    :class:`devilry.devilry_api.test_student_mixins.TestAuthAPIKeyStudentMixin`

        Test that no other than a student api key has access to the api.
        This mixin inherits from ``TestAuthAPIKeyMixin``, a read only student api key is already implemented here.

    :class:`devilry.devilry_api.test_examiner_mixins.TestAuthAPIKeyExaminerMixin`

        Test that no other than an examiner api key has access to the api.
        This mixin inherits from ``TestAuthAPIKeyMixin``, a read only student api key is already implemented here.

    :class:`devilry.devilry_api.test_admin_mixins.TestAuthAPIKeyAdminMixin`

        Test that no other than an admin api key has access to the api.
        This mixin inherits from ``TestAuthAPIKeyMixin``, a read only student api key is already implemented here.


Create a test class inside something like ``devilry_api/tests/test_my_view.py``::

    from model_mommy import mommy
    from rest_framework.test import APITestCase
    from devilry.devilry_api import devilry_api_mommy_factories as api_mommy
    from devilry.devilry_api.tests.mixins import test_student_mixins, api_test_helper, test_common_mixins
    from devilry.devilry_api.my_api.views.my_view import MyView

    class TestMyView(test_common_mixins.TestReadOnlyPermissionMixin,
                     test_student_mixins.TestAuthAPIKeyStudentMixin,
                     api_test_helper.TestCaseMixin,
                     APITestCase):
           viewclass = MyView #View that we are testing.

           def test_sanity(self):
               candidate = mommy.make('core.Candidate')
               apikey = api_mommy.api_key_student_permission_read(user=candidate.relatedstudent.user)
               response = self.mock_get_request(apikey=apikey.key)
               self.assertEqual(200, response.status_code)

.. _devilry_api-models:

**************
Database model
**************

.. py:currentmodule:: devilry_api.models

Functions
=========
:func:`devilry_api.models.generate_key` generates a random key
of size specified in :attr:`django.conf.settings.DEVILRY_API_KEYLENGTH`.

The model
=========
.. py:class:: APIKey

    The api key is used to authenticate a user upon the api with predefined permissions

    .. py:attribute:: key

        Database char field which contains the key itself.

    .. py:attribute:: user

        Database foreign key to the :class:`devilry_account.User` owner of the key.

    .. py:attribute:: creadet_datetime

        Database datetime field which stores the created timestamp of the key.

    .. py:attribute:: last_login_datetime

        Database datetime field which stores the last usage of the api key.
        Currently not in use.

    .. py:attribute:: user_agent

        Database text field which is supposed to store the user agent data of the last request.
        Currently not in use.

    .. py:attribute:: purpose

        Database char field which stores the purpose of the key, max length is 255

    .. py:attribute:: student_permission

        Database char field which tells what kind of student permission the key is granted.

        .. py:attribute:: STUDENT_NO_PERMISSION

            The key has no student permission.

        .. py:attribute:: STUDENT_PERMISSION_READ

            The key is granted GET, HEAD and OPTIONS for the student api

        .. py:attribute:: STUDENT_PERMISSION_WRITE

            The key is granted GET, HEAD, OPTIONS, POST, PUT, PATCH, DELETE for the examiner api

    .. py:attribute:: examiner_permission

        Database char field which tells what kind of examiner permission the key is granted.

        .. py:attribute:: EXAMINER_NO_PERMISSION

            The key has no examiner permission.

        .. py:attribute:: EXAMINER_PERMISSION_READ

            The key is granted GET, HEAD and OPTIONS for the examiner api

        .. py:attribute:: EXAMINER_PERMISSION_WRITE

            The key is granted GET, HEAD, OPTIONS, POST, PUT, PATCH, DELETE for the examiner api


    .. py:attribute:: admin_permission

        Database char field which tells what kind of admin permission the key is granted.

        .. py:attribute:: ADMIN_NO_PERMISSION

            The key has no admin permission.

        .. py:attribute:: ADMIN_PERMISSION_READ

            The key is granted GET, HEAD and OPTIONS for the examiner api

        .. py:attribute:: ADMIN_PERMISSION_WRITE

            The key is granted GET, HEAD, OPTIONS, POST, PUT, PATCH, DELETE for the admin api

    .. py:attribute:: keytype

        Database char field which tells us how long the key will last from creation.
        There are two choices.

        .. py:attribute:: LIFETIME_SHORT

            The key will last half a year.

        .. py:attribute:: LIFETIME_LONG

            The key will last a year.
