from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from cradmin_legacy import cradmin_testhelpers
from cradmin_legacy import crinstance
from model_bakery import baker

from devilry.apps.core.models import Subject
from devilry.devilry_account.models import PermissionGroup
from devilry.devilry_admin.views.dashboard import createsubject


class TestCreateView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = createsubject.CreateView

    def __make_superuser(self):
        return baker.make(settings.AUTH_USER_MODEL, is_superuser=True)

    def test_get_render_title(self):
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=self.__make_superuser())
        self.assertEqual("Create new course", mockresponse.selector.one("title").alltext_normalized)

    def test_get_render_h1(self):
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=self.__make_superuser())
        self.assertEqual("Create new course", mockresponse.selector.one("h1").alltext_normalized)

    def test_get_render_formfields(self):
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=self.__make_superuser())
        self.assertTrue(mockresponse.selector.exists("input[name=long_name]"))
        self.assertTrue(mockresponse.selector.exists("input[name=short_name]"))

    def test_get_permissiondenied_if_not_superuser(self):
        with self.assertRaises(PermissionDenied):
            self.mock_getrequest(requestuser=baker.make(settings.AUTH_USER_MODEL))

    def test_get_permissiondenied_if_subjectadmin(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make(
            "devilry_account.PermissionGroupUser",
            user=requestuser,
            permissiongroup=baker.make(
                "devilry_account.SubjectPermissionGroup",
                permissiongroup__grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN,
                subject=baker.make("core.Subject"),
            ).permissiongroup,
        )
        with self.assertRaises(PermissionDenied):
            self.mock_getrequest(requestuser=requestuser)

    def test_post_permissiondenied_if_not_superuser(self):
        with self.assertRaises(PermissionDenied):
            self.mock_postrequest(
                requestuser=baker.make(settings.AUTH_USER_MODEL),
                requestkwargs={
                    "data": {
                        "long_name": "Test subject",
                        "short_name": "testsubject",
                    }
                },
            )
        self.assertEqual(Subject.objects.count(), 0)

    def test_post_missing_short_name(self):
        mockresponse = self.mock_http200_postrequest_htmls(
            requestuser=self.__make_superuser(),
            requestkwargs={
                "data": {
                    "long_name": "Test subject",
                    "short_name": "",
                }
            },
        )
        self.assertEqual(Subject.objects.count(), 0)
        self.assertEqual(
            "This field is required.", mockresponse.selector.one("#error_1_id_short_name").alltext_normalized
        )

    def test_post_missing_long_name(self):
        mockresponse = self.mock_http200_postrequest_htmls(
            requestuser=self.__make_superuser(), requestkwargs={"data": {"long_name": "", "short_name": "testsubject"}}
        )
        self.assertEqual(Subject.objects.count(), 0)
        self.assertEqual(
            "This field is required.", mockresponse.selector.one("#error_1_id_long_name").alltext_normalized
        )

    def test_post_duplicate_short_name(self):
        mockresponse = self.mock_http200_postrequest_htmls(
            requestuser=self.__make_superuser(),
            requestkwargs={
                "data": {
                    "long_name": "Test subject",
                    "short_name": "",
                }
            },
        )
        self.assertEqual(Subject.objects.count(), 0)
        self.assertEqual(
            "This field is required.", mockresponse.selector.one("#error_1_id_short_name").alltext_normalized
        )

    def __valid_post_request(self, user=None):
        if not user:
            user = self.__make_superuser()
        mockresponse = self.mock_http302_postrequest(
            requestuser=user,
            requestkwargs={
                "data": {
                    "long_name": "Test subject",
                    "short_name": "testsubject",
                }
            },
        )
        created_subject = Subject.objects.get(short_name="testsubject")
        return created_subject, mockresponse

    def test_post_sanity(self):
        self.assertEqual(Subject.objects.count(), 0)
        created_subject, mockresponse = self.__valid_post_request()
        self.assertEqual(Subject.objects.count(), 1)
        self.assertEqual("Test subject", created_subject.long_name)
        self.assertEqual("testsubject", created_subject.short_name)

    def test_post_success_redirect(self):
        created_subject, mockresponse = self.__valid_post_request()
        self.assertEqual(
            mockresponse.response["location"],
            crinstance.reverse_cradmin_url(
                instanceid="devilry_admin_subjectadmin", appname="overview", roleid=created_subject.id
            ),
        )
