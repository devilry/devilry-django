from django import test
from django.conf import settings
from django.template import defaultfilters
from django.utils import timezone

from model_mommy import mommy
from django_cradmin import cradmin_testhelpers

from devilry.devilry_account.models import PermissionGroup
from devilry.devilry_admin.views.dashboard.student_feedbackfeed_wizard import assignment_list
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group.devilry_group_mommy_factories import make_first_feedbackset_in_group


class TestStudentAssignmentGroupListView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = assignment_list.StudentAssignmentGroupListView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_title(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        mockresponse = self.mock_http200_getrequest_htmls(
            viewkwargs={'user_id': testuser.id}
        )
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized, 'Assignments for testuser@example.com')

    def test_user_can_only_see_assignments_where_user_is_admin_on_subject(self):
        adminuser = mommy.make(settings.AUTH_USER_MODEL)
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        testsubject1 = mommy.make('core.Subject')
        testsubject2 = mommy.make('core.Subject')
        mommy.make('devilry_account.PermissionGroupUser', user=adminuser,
                   permissiongroup=mommy.make('devilry_account.SubjectPermissionGroup',
                                              permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                              subject=testsubject1).permissiongroup)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode__long_name='Accessible Assignment',
                                parentnode__parentnode__parentnode=testsubject1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode__long_name='Inaccessible Assignment',
                                parentnode__parentnode__parentnode=testsubject2)
        mommy.make('core.Candidate', assignment_group=testgroup1, relatedstudent__user=testuser)
        mommy.make('core.Candidate', assignment_group=testgroup2, relatedstudent__user=testuser)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=adminuser,
            viewkwargs={'user_id': testuser.id}
        ).selector
        self.assertEqual(selector.count('.django-cradmin-listbuilder-itemvalue'), 1)
        self.assertEqual(
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized,
            'Accessible Assignment')

    def test_user_can_only_see_assignments_where_user_is_admin_on_period(self):
        adminuser = mommy.make(settings.AUTH_USER_MODEL)
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        testsubject = mommy.make('core.Subject')
        testperiod1 = mommy.make('core.Period', parentnode=testsubject)
        testperiod2 = mommy.make('core.Period', parentnode=testsubject)
        mommy.make('devilry_account.PermissionGroupUser', user=adminuser,
                   permissiongroup=mommy.make('devilry_account.PeriodPermissionGroup',
                                              permissiongroup__grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN,
                                              period=testperiod1).permissiongroup)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode__long_name='Accessible Assignment',
                                parentnode__parentnode=testperiod1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode__long_name='Inaccessible Assignment',
                                parentnode__parentnode=testperiod2)
        mommy.make('core.Candidate', assignment_group=testgroup1, relatedstudent__user=testuser)
        mommy.make('core.Candidate', assignment_group=testgroup2, relatedstudent__user=testuser)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=adminuser,
            viewkwargs={'user_id': testuser.id}
        ).selector
        self.assertEqual(selector.count('.django-cradmin-listbuilder-itemvalue'), 1)
        self.assertEqual(
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized,
            'Accessible Assignment')

    def __make_simple_assignment_group(self, assignment_long_name='Assignment AAA'):
        group = mommy.make('core.AssignmentGroup',
                           parentnode__short_name='assingmentaaa',
                           parentnode__long_name=assignment_long_name,
                           parentnode__parentnode__short_name='periodaaa',
                           parentnode__parentnode__long_name='Period AAA',
                           parentnode__parentnode__start_time=timezone.now() - timezone.timedelta(days=100),
                           parentnode__parentnode__end_time=timezone.now() + timezone.timedelta(days=100),
                           parentnode__parentnode__parentnode__short_name='subjectaaa',
                           parentnode__parentnode__parentnode__long_name='Subject AAA')
        return group

    def test_default_ordering_by_deadline_datetime_ascending(self):
        now = timezone.now()
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode__long_name='Assignment A')
        make_first_feedbackset_in_group(group=testgroup1, deadline_datetime=now + timezone.timedelta(days=40))
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode__long_name='Assignment B')
        make_first_feedbackset_in_group(group=testgroup2, deadline_datetime=now + timezone.timedelta(days=30))
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode__long_name='Assignment C')
        mommy.make('core.Candidate', assignment_group=testgroup1, relatedstudent__user=testuser)
        mommy.make('core.Candidate', assignment_group=testgroup2, relatedstudent__user=testuser)
        mommy.make('core.Candidate', assignment_group=testgroup3, relatedstudent__user=testuser)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={'user_id': testuser.id}
        ).selector
        assignment_longname_list = [element.alltext_normalized for element in
                                    selector.list('.django-cradmin-listbuilder-itemvalue-titledescription-title')]
        self.assertListEqual(
            [
                'Assignment C',
                'Assignment B',
                'Assignment A'
            ],
            assignment_longname_list
        )

    def test_assignment_info_assignment_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        testgroup = self.__make_simple_assignment_group()
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=testuser)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={'user_id': testuser.id}
        ).selector
        self.assertEqual(
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized,
            testgroup.parentnode.long_name
        )

    def test_assignment_info_deadline_datetime(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        testgroup = self.__make_simple_assignment_group()
        testgroup.cached_data.last_feedbackset.deadline_datetime = timezone.now()
        testgroup.cached_data.last_feedbackset.save()
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=testuser)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={'user_id': testuser.id}
        ).selector
        self.assertEqual(
            selector.one('.devilry-admin-groupitem-deadline').alltext_normalized,
            'Deadline: {}'.format(
                defaultfilters.date(timezone.localtime(testgroup.cached_data.last_feedbackset.deadline_datetime),
                                    'DATETIME_FORMAT'))
        )

    def test_assignment_info_period_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        testgroup = self.__make_simple_assignment_group()
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=testuser)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={'user_id': testuser.id}
        ).selector
        self.assertEqual(
            selector.one('.devilry-admin-groupitem-by-assignment-periodname').alltext_normalized,
            'Semester: {}'.format(testgroup.parentnode.parentnode.long_name)
        )

    def test_assignment_info_subject_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        testgroup = self.__make_simple_assignment_group()
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=testuser)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={'user_id': testuser.id}
        ).selector
        self.assertEqual(
            selector.one('.devilry-admin-groupitem-by-assignment-subjectname').alltext_normalized,
            'Subject: {}'.format(testgroup.parentnode.parentnode.parentnode.long_name)
        )

    def test_assignment_info_delivery_status(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        testgroup = self.__make_simple_assignment_group()
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=testuser)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={'user_id': testuser.id}
        ).selector
        self.assertEqual(
            selector.one('.devilry-cradmin-groupitemvalue-status').alltext_normalized,
            'Status: {}'.format('waiting for feedback')
        )

    def test_search_candidate_in_group_nomatch(self):
        teststudent = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        testgroup = self.__make_simple_assignment_group()
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=teststudent)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={'user_id': teststudent.id, 'filters_string': 'search-NotInGroups'}
        ).selector
        self.assertEqual(selector.count('.django-cradmin-listbuilder-itemvalue'), 0)

    def test_search_other_candidate_in_group_fullname(self):
        teststudent = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        other_student = mommy.make(settings.AUTH_USER_MODEL, shortname='other@example.com', fullname='Other User')
        testgroup = self.__make_simple_assignment_group()
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=teststudent)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=other_student)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={'user_id': teststudent.id, 'filters_string': 'search-Other User'}
        ).selector
        self.assertEqual(selector.count('.django-cradmin-listbuilder-itemvalue'), 1)

    def test_search_other_candidate_in_group_shortname(self):
        teststudent = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        other_student = mommy.make(settings.AUTH_USER_MODEL, shortname='other@example.com', fullname='Other User')
        testgroup = self.__make_simple_assignment_group()
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=teststudent)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=other_student)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={'user_id': teststudent.id, 'filters_string': 'search-other@example.com'}
        ).selector
        self.assertEqual(selector.count('.django-cradmin-listbuilder-itemvalue'), 1)

    def test_search_examiner_nomatch(self):
        teststudent = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        examiner_user = mommy.make(settings.AUTH_USER_MODEL, shortname='examiner@example.com', fullname='Examiner')
        testgroup = self.__make_simple_assignment_group()
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=teststudent)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=examiner_user)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={'user_id': teststudent.id, 'filters_string': 'search-NoExaminerMatch'}
        ).selector
        self.assertEqual(selector.count('.django-cradmin-listbuilder-itemvalue'), 0)

    def test_search_examiner_fullname(self):
        teststudent = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        examiner_user = mommy.make(settings.AUTH_USER_MODEL, shortname='examiner@example.com', fullname='Examiner')
        testgroup = self.__make_simple_assignment_group()
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=teststudent)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=examiner_user)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={'user_id': teststudent.id, 'filters_string': 'search-Examiner'}
        ).selector
        self.assertEqual(selector.count('.django-cradmin-listbuilder-itemvalue'), 1)

    def test_search_examiner_shortname(self):
        teststudent = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        examiner_user = mommy.make(settings.AUTH_USER_MODEL, shortname='examiner@example.com', fullname='Examiner')
        testgroup = self.__make_simple_assignment_group()
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=teststudent)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=examiner_user)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={'user_id': teststudent.id, 'filters_string': 'search-examiner@example.com'}
        ).selector
        self.assertEqual(selector.count('.django-cradmin-listbuilder-itemvalue'), 1)

    def test_search_assignment_long_name(self):
        teststudent = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        testgroup = self.__make_simple_assignment_group()
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=teststudent)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={'user_id': teststudent.id, 'filters_string': 'search-{}'.format(testgroup.parentnode.long_name)}
        ).selector
        self.assertEqual(selector.count('.django-cradmin-listbuilder-itemvalue'), 1)

    def test_search_assignment_short_name(self):
        teststudent = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        testgroup = self.__make_simple_assignment_group()
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=teststudent)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={'user_id': teststudent.id, 'filters_string': 'search-{}'.format(testgroup.parentnode.short_name)}
        ).selector
        self.assertEqual(selector.count('.django-cradmin-listbuilder-itemvalue'), 1)

    def test_search_period_long_name(self):
        teststudent = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        testgroup = self.__make_simple_assignment_group()
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=teststudent)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={
                'user_id': teststudent.id,
                'filters_string': 'search-{}'.format(testgroup.parentnode.parentnode.long_name)
            }
        ).selector
        self.assertEqual(selector.count('.django-cradmin-listbuilder-itemvalue'), 1)

    def test_search_period_short_name(self):
        teststudent = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        testgroup = self.__make_simple_assignment_group()
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=teststudent)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={
                'user_id': teststudent.id,
                'filters_string': 'search-{}'.format(testgroup.parentnode.parentnode.short_name)
            }
        ).selector
        self.assertEqual(selector.count('.django-cradmin-listbuilder-itemvalue'), 1)

    def test_search_subject_long_name(self):
        teststudent = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        testgroup = self.__make_simple_assignment_group()
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=teststudent)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={
                'user_id': teststudent.id,
                'filters_string': 'search-{}'.format(testgroup.parentnode.parentnode.parentnode.long_name)
            }
        ).selector
        self.assertEqual(selector.count('.django-cradmin-listbuilder-itemvalue'), 1)

    def test_search_subject_short_name(self):
        teststudent = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        testgroup = self.__make_simple_assignment_group()
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=teststudent)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={
                'user_id': teststudent.id,
                'filters_string': 'search-{}'.format(testgroup.parentnode.parentnode.parentnode.short_name)
            }
        ).selector
        self.assertEqual(selector.count('.django-cradmin-listbuilder-itemvalue'), 1)

    def test_order_deadline_ascending(self):
        now = timezone.now()
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode__long_name='Assignment A')
        make_first_feedbackset_in_group(group=testgroup1, deadline_datetime=now + timezone.timedelta(days=40))
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode__long_name='Assignment B')
        make_first_feedbackset_in_group(group=testgroup2, deadline_datetime=now + timezone.timedelta(days=30))
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode__long_name='Assignment C')
        mommy.make('core.Candidate', assignment_group=testgroup1, relatedstudent__user=testuser)
        mommy.make('core.Candidate', assignment_group=testgroup2, relatedstudent__user=testuser)
        mommy.make('core.Candidate', assignment_group=testgroup3, relatedstudent__user=testuser)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={'user_id': testuser.id, 'filters_string': 'orderby_deadline-'}
        ).selector
        assignment_longname_list = [element.alltext_normalized for element in
                                    selector.list('.django-cradmin-listbuilder-itemvalue-titledescription-title')]
        self.assertListEqual(
            [
                'Assignment C',
                'Assignment B',
                'Assignment A'
            ],
            assignment_longname_list
        )

    def test_order_deadline_descending(self):
        now = timezone.now()
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode__long_name='Assignment A')
        make_first_feedbackset_in_group(group=testgroup1, deadline_datetime=now + timezone.timedelta(days=40))
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode__long_name='Assignment B')
        make_first_feedbackset_in_group(group=testgroup2, deadline_datetime=now + timezone.timedelta(days=30))
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode__long_name='Assignment C')
        mommy.make('core.Candidate', assignment_group=testgroup1, relatedstudent__user=testuser)
        mommy.make('core.Candidate', assignment_group=testgroup2, relatedstudent__user=testuser)
        mommy.make('core.Candidate', assignment_group=testgroup3, relatedstudent__user=testuser)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={'user_id': testuser.id, 'filters_string': 'orderby_deadline-deadline_descending'}
        ).selector
        assignment_longname_list = [element.alltext_normalized for element in
                                    selector.list('.django-cradmin-listbuilder-itemvalue-titledescription-title')]
        self.assertListEqual(
            [
                'Assignment A',
                'Assignment B',
                'Assignment C'
            ],
            assignment_longname_list
        )

    def test_filter_semesters_blank_shows_all_periods(self):
        testperiod_old = mommy.make_recipe('devilry.apps.core.period_old')
        testperiod_active = mommy.make_recipe('devilry.apps.core.period_active')
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        testgroup_old_period = mommy.make('core.AssignmentGroup',
                                          parentnode__long_name='Assignment Old',
                                          parentnode__parentnode=testperiod_old)
        testgroup_active_period = mommy.make('core.AssignmentGroup',
                                             parentnode__long_name='Assignment Active',
                                             parentnode__parentnode=testperiod_active)
        mommy.make('core.Candidate', assignment_group=testgroup_old_period, relatedstudent__user=testuser)
        mommy.make('core.Candidate', assignment_group=testgroup_active_period, relatedstudent__user=testuser)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={'user_id': testuser.id, 'filters_string': 'semester_is_active-'}
        ).selector
        self.assertEqual(selector.count('.django-cradmin-listbuilder-itemvalue'), 2)

    def test_filter_active_periods(self):
        testperiod_old = mommy.make_recipe('devilry.apps.core.period_old')
        testperiod_active = mommy.make_recipe('devilry.apps.core.period_active')
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        testgroup_old_period = mommy.make('core.AssignmentGroup',
                                          parentnode__long_name='Assignment Old',
                                          parentnode__parentnode=testperiod_old)
        testgroup_active_period = mommy.make('core.AssignmentGroup',
                                             parentnode__long_name='Assignment Active',
                                             parentnode__parentnode=testperiod_active)
        mommy.make('core.Candidate', assignment_group=testgroup_old_period, relatedstudent__user=testuser)
        mommy.make('core.Candidate', assignment_group=testgroup_active_period, relatedstudent__user=testuser)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={'user_id': testuser.id, 'filters_string': 'semester_is_active-true'}
        ).selector
        self.assertEqual(selector.count('.django-cradmin-listbuilder-itemvalue'), 1)
        self.assertEqual(
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized,
            'Assignment Active'
        )

    def test_filter_inactive_periods(self):
        testperiod_old = mommy.make_recipe('devilry.apps.core.period_old')
        testperiod_active = mommy.make_recipe('devilry.apps.core.period_active')
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        testgroup_old_period = mommy.make('core.AssignmentGroup',
                                          parentnode__long_name='Assignment Old',
                                          parentnode__parentnode=testperiod_old)
        testgroup_active_period = mommy.make('core.AssignmentGroup',
                                             parentnode__long_name='Assignment Active',
                                             parentnode__parentnode=testperiod_active)
        mommy.make('core.Candidate', assignment_group=testgroup_old_period, relatedstudent__user=testuser)
        mommy.make('core.Candidate', assignment_group=testgroup_active_period, relatedstudent__user=testuser)
        selector = self.mock_http200_getrequest_htmls(
            requestuser=mommy.make(settings.AUTH_USER_MODEL, is_superuser=True),
            viewkwargs={'user_id': testuser.id, 'filters_string': 'semester_is_active-false'}
        ).selector
        self.assertEqual(selector.count('.django-cradmin-listbuilder-itemvalue'), 1)
        self.assertEqual(
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized,
            'Assignment Old'
        )

    def test_query_count(self):
        adminuser = mommy.make(settings.AUTH_USER_MODEL)
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@example.com', fullname='Test User')
        testsubjects = mommy.make('core.Subject', _quantity=10)
        for testsubject in testsubjects:
            mommy.make('devilry_account.PermissionGroupUser', user=adminuser,
                       permissiongroup=mommy.make('devilry_account.SubjectPermissionGroup',
                                                  permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                                  subject=testsubject).permissiongroup)

            # Create ten assignments for each subject
            for num in range(10):
                testgroup = mommy.make('core.AssignmentGroup', parentnode__long_name='Accessible Assignment',
                                       parentnode__parentnode__parentnode=testsubject)
                mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=testuser)
        with self.assertNumQueries(6):
            selector = self.mock_http200_getrequest_htmls(
                requestuser=adminuser,
                viewkwargs={'user_id': testuser.id}
            ).selector
            self.assertEqual(selector.count('.django-cradmin-listbuilder-itemvalue'), 15)
