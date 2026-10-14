from unittest import mock
from django import test
from django.conf import settings

from model_bakery import baker
from cradmin_legacy import cradmin_testhelpers

from devilry.devilry_account.models import PermissionGroup
from devilry.devilry_admin.views.dashboard.student_feedbackfeed_wizard import student_list


class TestStudentListView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = student_list.UserListView

    def __make_periodadmin(self, period):
        adminuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make(
            "devilry_account.PermissionGroupUser",
            user=adminuser,
            permissiongroup=baker.make(
                "devilry_account.PeriodPermissionGroup",
                permissiongroup__grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN,
                period=period,
            ).permissiongroup,
        )
        return adminuser

    def __make_subjectadmin(self, subject):
        adminuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make(
            "devilry_account.PermissionGroupUser",
            user=adminuser,
            permissiongroup=baker.make(
                "devilry_account.SubjectPermissionGroup",
                permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                subject=subject,
            ).permissiongroup,
        )
        return adminuser

    def __get_titles(self, mockresponse):
        return [
            element.alltext_normalized
            for element in mockresponse.selector.list(".cradmin-legacy-listbuilder-itemvalue-titledescription-title")
        ]

    def test_title(self):
        testperiod = baker.make("core.Period")
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=self.__make_periodadmin(period=testperiod))
        self.assertEqual(mockresponse.selector.one("title").alltext_normalized, "Select a student")

    def test_only_users_with_relatedstudent_are_listed(self):
        testperiod = baker.make("core.Period")
        baker.make(settings.AUTH_USER_MODEL, shortname="notstudentuser")
        baker.make("core.RelatedStudent", period=testperiod, user__shortname="studentuser")
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=self.__make_periodadmin(period=testperiod))
        self.assertEqual(mockresponse.selector.count(".cradmin-legacy-listbuilder-itemvalue-titledescription-title"), 1)
        self.assertContains(mockresponse.response, "studentuser")
        self.assertNotContains(mockresponse.response, "notstudentuser")

    def test_user_without_admin_permissions_sees_no_students(self):
        baker.make("core.RelatedStudent", user__shortname="studentuser")
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=baker.make(settings.AUTH_USER_MODEL))
        self.assertEqual(mockresponse.selector.count(".cradmin-legacy-listbuilder-itemvalue"), 0)
        self.assertNotContains(mockresponse.response, "studentuser")

    def test_periodadmin_only_sees_students_in_period_where_user_is_admin(self):
        testperiod1 = baker.make("core.Period")
        testperiod2 = baker.make("core.Period")
        baker.make("core.RelatedStudent", period=testperiod1, user__shortname="accessiblestudent")
        baker.make("core.RelatedStudent", period=testperiod2, user__shortname="inaccessiblestudent")
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=self.__make_periodadmin(period=testperiod1))
        self.assertEqual(mockresponse.selector.count(".cradmin-legacy-listbuilder-itemvalue"), 1)
        self.assertContains(mockresponse.response, "accessiblestudent")
        self.assertNotContains(mockresponse.response, "inaccessiblestudent")

    def test_subjectadmin_sees_students_in_all_periods_within_subject(self):
        testsubject1 = baker.make("core.Subject")
        testsubject2 = baker.make("core.Subject")
        baker.make(
            "core.RelatedStudent",
            period=baker.make("core.Period", parentnode=testsubject1),
            user__shortname="accessiblestudent1",
        )
        baker.make(
            "core.RelatedStudent",
            period=baker.make("core.Period", parentnode=testsubject1),
            user__shortname="accessiblestudent2",
        )
        baker.make(
            "core.RelatedStudent",
            period=baker.make("core.Period", parentnode=testsubject2),
            user__shortname="inaccessiblestudent",
        )
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=self.__make_subjectadmin(subject=testsubject1))
        self.assertEqual(mockresponse.selector.count(".cradmin-legacy-listbuilder-itemvalue"), 2)
        self.assertContains(mockresponse.response, "accessiblestudent1")
        self.assertContains(mockresponse.response, "accessiblestudent2")
        self.assertNotContains(mockresponse.response, "inaccessiblestudent")

    def test_superuser_sees_students_in_all_periods(self):
        baker.make("core.RelatedStudent", user__shortname="studenta")
        baker.make("core.RelatedStudent", user__shortname="studentb")
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=baker.make(settings.AUTH_USER_MODEL, is_superuser=True)
        )
        self.assertEqual(mockresponse.selector.count(".cradmin-legacy-listbuilder-itemvalue"), 2)

    def test_student_in_multiple_periods_is_only_listed_once(self):
        testsubject = baker.make("core.Subject")
        testuser = baker.make(settings.AUTH_USER_MODEL, shortname="studentuser")
        baker.make("core.RelatedStudent", period=baker.make("core.Period", parentnode=testsubject), user=testuser)
        baker.make("core.RelatedStudent", period=baker.make("core.Period", parentnode=testsubject), user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=self.__make_subjectadmin(subject=testsubject))
        self.assertEqual(mockresponse.selector.count(".cradmin-legacy-listbuilder-itemvalue"), 1)

    def test_list_users(self):
        testperiod = baker.make("core.Period")
        baker.make("core.RelatedStudent", period=testperiod, user__shortname="a", user__fullname="A")
        baker.make("core.RelatedStudent", period=testperiod, user__shortname="b", user__fullname="B")
        baker.make("core.RelatedStudent", period=testperiod, user__shortname="c", user__fullname="C")
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=self.__make_periodadmin(period=testperiod))
        fullname_list = self.__get_titles(mockresponse)
        shortname_list = [
            element.alltext_normalized
            for element in mockresponse.selector.list(
                ".cradmin-legacy-listbuilder-itemvalue-titledescription-description"
            )
        ]
        self.assertEqual(mockresponse.selector.count(".cradmin-legacy-listbuilder-itemvalue"), 3)
        self.assertIn("A", fullname_list)
        self.assertIn("B", fullname_list)
        self.assertIn("C", fullname_list)
        self.assertIn("a", shortname_list)
        self.assertIn("b", shortname_list)
        self.assertIn("c", shortname_list)

    def test_search_no_match(self):
        testperiod = baker.make("core.Period")
        baker.make("core.RelatedStudent", period=testperiod, user__shortname="a", user__fullname="A")
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=self.__make_periodadmin(period=testperiod), viewkwargs={"filters_string": "search-No match"}
        )
        self.assertEqual(0, mockresponse.selector.count(".cradmin-legacy-listbuilder-itemvalue"))

    def test_search_match_fullname(self):
        testperiod = baker.make("core.Period")
        baker.make("core.RelatedStudent", period=testperiod, user__shortname="shortnamea", user__fullname="FullnameA")
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=self.__make_periodadmin(period=testperiod), viewkwargs={"filters_string": "search-FullnameA"}
        )
        self.assertEqual(1, mockresponse.selector.count(".cradmin-legacy-listbuilder-itemvalue"))

    def test_search_match_shortname(self):
        testperiod = baker.make("core.Period")
        baker.make("core.RelatedStudent", period=testperiod, user__shortname="shortnamea", user__fullname="FullnameA")
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=self.__make_periodadmin(period=testperiod), viewkwargs={"filters_string": "search-shortnamea"}
        )
        self.assertEqual(1, mockresponse.selector.count(".cradmin-legacy-listbuilder-itemvalue"))

    def test_search_does_not_match_student_in_other_period(self):
        testperiod = baker.make("core.Period")
        baker.make("core.RelatedStudent", user__shortname="shortnamea", user__fullname="FullnameA")
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=self.__make_periodadmin(period=testperiod), viewkwargs={"filters_string": "search-FullnameA"}
        )
        self.assertEqual(0, mockresponse.selector.count(".cradmin-legacy-listbuilder-itemvalue"))

    def test_backlink(self):
        testperiod = baker.make("core.Period")
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=self.__make_periodadmin(period=testperiod))
        self.assertEqual(1, len(mockresponse.request.cradmin_instance.reverse_url.call_args_list))
        self.assertEqual(
            mock.call(appname="overview", args=(), kwargs={}, viewname="INDEX"),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[0],
        )

    def test_pagination(self):
        testperiod = baker.make("core.Period")
        baker.make("core.RelatedStudent", period=testperiod, _quantity=50)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=self.__make_periodadmin(period=testperiod))
        self.assertEqual(mockresponse.selector.count(".cradmin-legacy-listbuilder-itemvalue"), 35)

    def test_query_count(self):
        testperiod = baker.make("core.Period")
        requestuser = self.__make_periodadmin(period=testperiod)
        baker.make("core.RelatedStudent", period=testperiod, _quantity=10)
        with self.assertNumQueries(4):
            self.mock_http200_getrequest_htmls(requestuser=requestuser)
        baker.make("core.RelatedStudent", period=testperiod, _quantity=90)
        with self.assertNumQueries(4):
            self.mock_http200_getrequest_htmls(requestuser=requestuser)
        baker.make("core.RelatedStudent", period=testperiod, _quantity=400)
        with self.assertNumQueries(4):
            self.mock_http200_getrequest_htmls(requestuser=requestuser)
