from __future__ import unicode_literals
import mock
from django.conf import settings
from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from django_cradmin import crinstance
from model_mommy import mommy

from devilry.apps.core.models import Assignment
from devilry.apps.core.mommy_recipes import ASSIGNMENT_ACTIVEPERIOD_START_FIRST_DEADLINE, ACTIVE_PERIOD_START
from devilry.devilry_admin.views.period import overview
from devilry.devilry_account import models as account_models
from devilry.utils import datetimeutils


class TestOverview(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = overview.Overview

    def __make_period_admin_user(self, period):
        admin_user = mommy.make(settings.AUTH_USER_MODEL)
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup', period=period)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=admin_user,
                   permissiongroup=periodpermissiongroup.permissiongroup)
        return admin_user

    def __make_subject_admin_user(self, subject, as_department_admin=False):
        if as_department_admin:
            permissiongroup_type = account_models.PermissionGroup.GROUPTYPE_DEPARTMENTADMIN
        else:
            permissiongroup_type = account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN
        admin_user = mommy.make(settings.AUTH_USER_MODEL)
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            permissiongroup__grouptype=permissiongroup_type, subject=subject)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=admin_user,
                   permissiongroup=subjectpermissiongroup.permissiongroup)
        return admin_user

    def test_title(self):
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual('testsubject.testperiod',
                         mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testperiod = mommy.make('core.Period',
                                parentnode__long_name='Test Subject',
                                long_name='Test Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(u'Test Period \u2014 Test Subject',
                         mockresponse.selector.one('h1').alltext_normalized)

    def test_no_students_and_examiners_on_semester_meta(self):
        testperiod = mommy.make('core.Period',
                                parentnode__long_name='Test Subject',
                                long_name='Test Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(mockresponse.selector.one('#id_devilry-num-relatedusers-on-period').alltext_normalized,
                         '0 student(s) and 0 examiner(s) on the semester')

    def test_num_students_and_examiners_on_semester_meta(self):
        testperiod = mommy.make('core.Period',
                                parentnode__long_name='Test Subject',
                                long_name='Test Period')
        mommy.make('core.RelatedStudent', period=testperiod, _quantity=8)
        mommy.make('core.RelatedExaminer', period=testperiod, _quantity=4)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(mockresponse.selector.one('#id_devilry-num-relatedusers-on-period').alltext_normalized,
                         '8 student(s) and 4 examiner(s) on the semester')

    def test_createassignment_link_text(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual('Create new assignment',
                         mockresponse.selector.one(
                             '#devilry_admin_period_createassignment_link').alltext_normalized)

    def test_link_urls(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(8, len(mockresponse.request.cradmin_instance.reverse_url.call_args_list))
        self.assertEqual(
                mock.call(appname='edit', args=(), viewname='INDEX', kwargs={}),
                mockresponse.request.cradmin_instance.reverse_url.call_args_list[0])
        self.assertEqual(
                mock.call(appname='createassignment', args=(), viewname='INDEX', kwargs={}),
                mockresponse.request.cradmin_instance.reverse_url.call_args_list[1])
        self.assertEqual(
                mock.call(appname='students', args=(), viewname='INDEX', kwargs={}),
                mockresponse.request.cradmin_instance.reverse_url.call_args_list[2])
        self.assertEqual(
                mock.call(appname='examiners', args=(), viewname='INDEX', kwargs={}),
                mockresponse.request.cradmin_instance.reverse_url.call_args_list[3])
        self.assertEquals(
            mock.call(appname='manage_tags', args=(), viewname='INDEX', kwargs={}),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[4])
        self.assertEqual(
                mock.call(appname='admins', args=(), viewname='INDEX', kwargs={}),
                mockresponse.request.cradmin_instance.reverse_url.call_args_list[5])
        self.assertEqual(
            mock.call(appname='overview_all_results', args=(), viewname='INDEX', kwargs={}),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[6])
        self.assertEqual(
                mock.call(appname='qualifiesforexam', args=(), viewname='INDEX', kwargs={}),
                mockresponse.request.cradmin_instance.reverse_url.call_args_list[7])

    def test_assignmentlist_no_assignments(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertFalse(mockresponse.selector.exists('#devilry_admin_period_overview_assignmentlist'))

    def test_assignmentlist_itemrendering_name(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        periodadmin_user = self.__make_period_admin_user(period=testperiod)
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=testperiod,
                          long_name='Test Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod, requestuser=periodadmin_user)
        self.assertEqual('Test Assignment',
                         mockresponse.selector.one(
                             '.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_assignmentlist_itemrendering_url(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        periodadmin_user = self.__make_period_admin_user(period=testperiod)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           parentnode=testperiod,
                                           long_name='Test Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod, requestuser=periodadmin_user)
        self.assertEqual(crinstance.reverse_cradmin_url(instanceid='devilry_admin_assignmentadmin',
                                                        appname='overview',
                                                        roleid=testassignment.id),
                         mockresponse.selector.one(
                             '.devilry-admin-period-overview-assignmentitemframe')['href'])

    def test_assignmentlist_itemrendering_first_deadline(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        periodadmin_user = self.__make_period_admin_user(period=testperiod)
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', parentnode=testperiod)
        with self.settings(DATETIME_FORMAT=datetimeutils.ISODATETIME_DJANGOFORMAT, USE_L10N=False):
            mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod, requestuser=periodadmin_user)
        self.assertEqual(datetimeutils.isoformat_noseconds(ASSIGNMENT_ACTIVEPERIOD_START_FIRST_DEADLINE),
                         mockresponse.selector.one(
                             '.devilry-admin-period-overview-assignment-first-deadline-value').alltext_normalized)

    def test_assignmentlist_itemrendering_publishing_time(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        periodadmin_user = self.__make_period_admin_user(period=testperiod)
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=testperiod)
        with self.settings(DATETIME_FORMAT=datetimeutils.ISODATETIME_DJANGOFORMAT, USE_L10N=False):
            mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod, requestuser=periodadmin_user)
        self.assertEqual(datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_START),
                         mockresponse.selector.one(
                             '.devilry-admin-period-overview-assignment-publishing-time-value').alltext_normalized)

    def test_assignmentlist_ordering(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        periodadmin_user = self.__make_period_admin_user(period=testperiod)
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=testperiod,
                          long_name='Assignment 1')
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_middle',
                          parentnode=testperiod,
                          long_name='Assignment 2')
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end',
                          parentnode=testperiod,
                          long_name='Assignment 3')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod, requestuser=periodadmin_user)
        assignmentnames = [
            element.alltext_normalized
            for element in mockresponse.selector.list(
                    '.django-cradmin-listbuilder-itemvalue-titledescription-title')]
        self.assertEqual([
            'Assignment 3',
            'Assignment 2',
            'Assignment 1',
        ], assignmentnames)

    def test_periodlist_only_assignments_in_period(self):
        testperiod = mommy.make('core.Period')
        otherperiod = mommy.make('core.Period')
        periodadmin_user_testperiod = self.__make_period_admin_user(period=testperiod)
        self.__make_period_admin_user(period=otherperiod)
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=testperiod,
                          long_name='Testperiod Assignment 1')
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=otherperiod,
                          long_name='Otherperiod Assignment 1')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=periodadmin_user_testperiod)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue-titledescription-title')
        )
        self.assertEqual(
            'Testperiod Assignment 1',
            mockresponse.selector.one(
                    '.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized
        )

    def test_period_admin_can_not_see_semi_anonymous_assignments(self):
        testperiod = mommy.make('core.Period')
        periodadmin_user = self.__make_period_admin_user(period=testperiod)
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=testperiod,
                          anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS,
                          long_name='Testperiod Assignment 1')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=periodadmin_user)
        self.assertFalse(mockresponse.selector.exists('#devilry_admin_period_overview_assignmentlist'))

    def test_period_admin_can_not_see_fully_anonymous_assignments(self):
        testperiod = mommy.make('core.Period')
        periodadmin_user = self.__make_period_admin_user(period=testperiod)
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=testperiod,
                          anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS,
                          long_name='Testperiod Assignment 1')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=periodadmin_user)
        self.assertFalse(mockresponse.selector.exists('#devilry_admin_period_overview_assignmentlist'))

    def test_subject_admin_can_see_semi_anonymous_assignments(self):
        testperiod = mommy.make('core.Period')
        subjectadmin_user = self.__make_subject_admin_user(subject=testperiod.parentnode)
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=testperiod,
                          anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS,
                          long_name='Testperiod Assignment 1')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=subjectadmin_user)
        self.assertFalse(mockresponse.selector.exists('#devilry_admin_period_overview_assignmentlist'))

    def test_subject_admin_can_see_fully_anonymous_assignments(self):
        testperiod = mommy.make('core.Period')
        subjectadmin_user = self.__make_subject_admin_user(subject=testperiod.parentnode)
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=testperiod,
                          anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS,
                          long_name='Testperiod Assignment 1')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=subjectadmin_user)
        self.assertFalse(mockresponse.selector.exists('#devilry_admin_period_overview_assignmentlist'))

    def test_department_admin_can_see_semi_anonymous_assignments(self):
        testperiod = mommy.make('core.Period')
        departmentadmin_user = self.__make_subject_admin_user(subject=testperiod.parentnode, as_department_admin=True)
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=testperiod,
                          anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS,
                          long_name='Testperiod Assignment 1')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=departmentadmin_user)
        self.assertFalse(mockresponse.selector.exists('#devilry_admin_period_overview_assignmentlist'))

    def test_department_admin_can_see_fully_anonymous_assignments(self):
        testperiod = mommy.make('core.Period')
        departmentadmin_user = self.__make_subject_admin_user(subject=testperiod.parentnode, as_department_admin=True)
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=testperiod,
                          anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS,
                          long_name='Testperiod Assignment 1')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=departmentadmin_user)
        self.assertFalse(mockresponse.selector.exists('#devilry_admin_period_overview_assignmentlist'))

    def test_num_queries(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        periodadmin_user = self.__make_period_admin_user(period=testperiod)
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=testperiod, _quantity=10)
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_middle',
                          parentnode=testperiod, _quantity=10)
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end',
                          parentnode=testperiod, _quantity=10)
        mommy.make('core.RelatedStudent', period=testperiod, _quantity=50)
        mommy.make('core.RelatedExaminer', period=testperiod, _quantity=50)
        with self.assertNumQueries(4):
            self.mock_http200_getrequest_htmls(cradmin_role=testperiod, requestuser=periodadmin_user)