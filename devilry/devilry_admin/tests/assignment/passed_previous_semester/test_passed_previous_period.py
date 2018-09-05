import mock
from django.contrib import messages
from django.http import Http404
from django.template import defaultfilters
from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from devilry.apps.core.models import Assignment
from devilry.apps.core.mommy_recipes import OLD_PERIOD_START, OLD_PERIOD_END
from devilry.devilry_admin.views.assignment.passed_previous_period import passed_previous_period
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group.models import FeedbacksetPassedPreviousPeriod


class TestSelectPeriodViewAnonymization(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = passed_previous_period.SelectPeriodView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_anonymizationmode_fully_departmentadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))

    def test_404_anonymizationmode_fully_subjectadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'))

    def test_404_anonymizationmode_fully_periodadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('periodadmin'))

    def test_anonymizationmode_semi_departmentadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))

    def test_anonymizationmode_semi_subjectadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'))

    def test_404_anonymizationmode_semi_periodadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('periodadmin'))

    def test_anonymizationmode_off_departmentadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))

    def test_anonymizationmode_off_subjectadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'))

    def test_anonymizationmode_off_period(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('periodadmin'))


class TestSelectPeriodView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = passed_previous_period.SelectPeriodView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_title(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        self.assertIn(
            'Select the earliest semester you want to approve for',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        self.assertIn(
            'Step 1 of 3: select the earliest semester you want to approve for',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_submit_button_text_sanity(self):
        period = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='cool',
            parentnode__short_name='s16',
            parentnode__long_name='spring16'
        ).parentnode
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='cool',
            parentnode__short_name='s17',
            parentnode__long_name='spring17',
            parentnode__parentnode=period.parentnode
        )
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        self.assertIn(
            'Next',
            mockresponse.selector.one('#submit-id-next').alltext_normalized)

    def test_no_previous_period_sanity(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        self.assertTrue(mockresponse.selector.one('.test-no-previos-period'))

    def test_no_previous_period_message(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        self.assertEqual(
            mockresponse.selector.one('.test-no-previos-period').alltext_normalized,
            'There are no prior semesters connected to this assignment.'
        )

    def test_select_previous_period_simple(self):
        period = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='cool',
            parentnode__short_name='s16',
            parentnode__long_name='spring16'
        ).parentnode
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='cool',
            parentnode__short_name='s17',
            parentnode__long_name='spring17',
            parentnode__parentnode=period.parentnode
        )
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        selectlist = [elem.alltext_normalized.split(' (')[0] for elem in mockresponse.selector.list('.controls  > .radio')]
        self.assertEqual(1, len(selectlist))
        self.assertNotIn(
            '{} - {}'.format(testassignment.parentnode.short_name, testassignment.parentnode.long_name),
            selectlist
        )
        self.assertIn(
            '{} - {}'.format(period.short_name, period.long_name),
            selectlist
        )

    def test_select_previous_period_multiple(self):
        period1 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='cool',
            parentnode__short_name='asd',
            parentnode__long_name='Adfsad'
        ).parentnode
        period2 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_middle',
            short_name='cool',
            parentnode__short_name='ghdfg',
            parentnode__long_name='Oijjop',
            parentnode__parentnode=period1.parentnode
        ).parentnode
        period3 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_end',
            short_name='cool',
            parentnode__short_name='polmfhg',
            parentnode__long_name='KOPkop',
            parentnode__parentnode=period1.parentnode
        ).parentnode
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='cool',
            parentnode__short_name='s17',
            parentnode__long_name='spring17',
            parentnode__parentnode=period1.parentnode
        )
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        selectlist = [elem.alltext_normalized.split(' (')[0] for elem in mockresponse.selector.list('.controls  > .radio')]
        self.assertEqual(3, len(selectlist))
        self.assertNotIn(
            '{} - {}'.format(testassignment.parentnode.short_name, testassignment.parentnode.long_name),
            selectlist
        )
        self.assertIn(
            '{} - {}'.format(
                period1.short_name,
                period1.long_name
            ),
            selectlist
        )
        self.assertIn(
            '{} - {}'.format(
                period2.short_name,
                period2.long_name
            ),
            selectlist
        )
        self.assertIn(
            '{} - {}'.format(
                period3.short_name,
                period3.long_name
            ),
            selectlist
        )

    def test_select_previous_period_multiple_not_in(self):
        period1 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='assignment1',
            parentnode__short_name='asd',
            parentnode__long_name='Adfsad'
        ).parentnode
        period2 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_middle',
            short_name='cool',
            parentnode__short_name='ghdfg',
            parentnode__long_name='Oijjop'
        ).parentnode
        period3 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_end',
            short_name='cool',
            parentnode__short_name='polmfhg',
            parentnode__long_name='KOPkop',
            parentnode__parentnode=period1.parentnode
        ).parentnode
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='cool',
            parentnode__short_name='s17',
            parentnode__long_name='spring17',
            parentnode__parentnode=period1.parentnode
        )
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        selectlist = [elem.alltext_normalized.split(' (')[0] for elem in mockresponse.selector.list('.controls  > .radio')]
        self.assertEqual(1, len(selectlist))
        self.assertNotIn(
            '{} - {}'.format(testassignment.parentnode.short_name, testassignment.parentnode.long_name),
            selectlist
        )
        self.assertNotIn(
            '{} - {}'.format(period1.short_name, period1.long_name),
            selectlist
        )
        self.assertNotIn(
            '{} - {}'.format(period2.short_name, period2.long_name),
            selectlist
        )
        self.assertIn(
            '{} - {}'.format(period3.short_name, period3.long_name),
            selectlist
        )

    def test_select_previous_period_multiple_future_not_in(self):
        period1 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_middle',
            short_name='cool',
            parentnode__short_name='ghdfg',
            parentnode__long_name='Oijjop'
        ).parentnode
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='cool',
            parentnode__short_name='s17',
            parentnode__long_name='spring17',
            parentnode__parentnode=period1.parentnode
        )
        period2 = mommy.make_recipe(
            'devilry.apps.core.assignment_futureperiod_start',
            short_name='cool',
            parentnode__short_name='sdgf',
            parentnnode__long_name='opkjmdgf',
            parentnode__parentnode=period1.parentnode
        ).parentnode
        period3 = mommy.make_recipe(
            'devilry.apps.core.assignment_futureperiod_middle',
            short_name='cool',
            parentnode__short_name='hgdf',
            parentnnode__long_name='asdads',
            parentnode__parentnode=period1.parentnode
        ).parentnode

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        selectlist = [elem.alltext_normalized.split(' (')[0] for elem in mockresponse.selector.list('.controls  > .radio')]
        self.assertEqual(1, len(selectlist))
        self.assertNotIn(
            '{} - {}'.format(testassignment.parentnode.short_name, testassignment.parentnode.long_name),
            selectlist
        )
        self.assertIn(
            '{} - {}'.format(period1.short_name, period1.long_name),
            selectlist
        )
        self.assertNotIn(
            '{} - {}'.format(period2.short_name, period2.long_name),
            selectlist
        )
        self.assertNotIn(
            '{} - {}'.format(period3.short_name, period3.long_name),
            selectlist
        )

    def test_links(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        self.assertEquals(1, len(mockresponse.request.cradmin_instance.reverse_url.call_args_list))
        self.assertEqual(
            mock.call(appname='passed_previous_period', args=(), kwargs={}, viewname='INDEX'),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[0]
        )


class TestAssignmentViewAnonymization(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = passed_previous_period.PassedPreviousAssignmentView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_anonymizationmode_fully_departmentadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'period_id': testassignment.parentnode.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))

    def test_404_anonymizationmode_fully_subjectadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                viewkwargs={'period_id': testassignment.parentnode.id},
                cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'))

    def test_404_anonymizationmode_fully_periodadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                viewkwargs={'period_id': testassignment.parentnode.id},
                cradmin_instance=self.__mockinstance_with_devilryrole('periodadmin'))

    def test_anonymizationmode_semi_departmentadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'period_id': testassignment.parentnode.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))

    def test_anonymizationmode_semi_subjectadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'period_id': testassignment.parentnode.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'))

    def test_404_anonymizationmode_semi_periodadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                viewkwargs={'period_id': testassignment.parentnode.id},
                cradmin_instance=self.__mockinstance_with_devilryrole('periodadmin'))

    def test_anonymizationmode_off_departmentadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'period_id': testassignment.parentnode.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))

    def test_anonymizationmode_off_subjectadmin(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'period_id': testassignment.parentnode.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'))

    def test_anonymizationmode_off_period(self):
        testassignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'period_id': testassignment.parentnode.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('periodadmin'))


class TestPassedPreviousAssignmentView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = passed_previous_period.PassedPreviousAssignmentView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_title(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'period_id': testassignment.parentnode.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        self.assertIn(
            'Confirm assignments',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'period_id': testassignment.parentnode.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        self.assertIn(
            'Step 2 of 3: Confirm assignments',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_next_button(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'period_id': testassignment.parentnode.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        self.assertIn(
            'Next',
            mockresponse.selector.one('.btn-primary').alltext_normalized)

    def test_links(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'period_id': testassignment.parentnode.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )

        self.assertEquals(2, len(mockresponse.request.cradmin_instance.reverse_url.call_args_list))
        self.assertEqual(
            mock.call(appname='passed_previous_period', args=(), kwargs={}, viewname='INDEX'),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[0]
        )
        self.assertEqual(
            mock.call(appname='passed_previous_period', args=(),
                      kwargs={'period_id': testassignment.parentnode.id}, viewname='confirm'),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[1]
        )


class TestPassedPreviousAssignmentViewListbuilder(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = passed_previous_period.PassedPreviousAssignmentView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_simple_description(self):
        testassignment1 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='cool',
            parentnode__short_name='s16',
            parentnode__long_name='spring16',
            max_points=2,
            passing_grade_min_points=1
        )
        testassignment2 = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='cool',
            parentnode__short_name='s17',
            parentnode__long_name='spring17',
            parentnode__parentnode=testassignment1.parentnode.parentnode
        )
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment2,
            viewkwargs={'period_id': testassignment1.parentnode.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        valuelist = [elem.alltext_normalized for elem in mockresponse.selector.list(
            '.django-cradmin-listbuilder-itemvalue-titledescription-description')]
        self.assertEqual(2, len(valuelist))
        self.assertIn(
            '{}/{} (max points/passing grade)'.format(testassignment1.max_points,
                                                      testassignment1.passing_grade_min_points),
            valuelist
        )

    def test_simple(self):
        testassignment1 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='cool',
            parentnode__short_name='s16',
            parentnode__long_name='spring16'
        )
        testassignment2 = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='cool',
            parentnode__short_name='s17',
            parentnode__long_name='spring17',
            parentnode__parentnode=testassignment1.parentnode.parentnode
        )
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment2,
            viewkwargs={'period_id': testassignment1.parentnode.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )

        valuelist = [elem.alltext_normalized for elem in mockresponse.selector.list(
            '.django-cradmin-listbuilder-itemvalue-titledescription-title')]
        self.assertEqual(1, len(valuelist))
        self.assertNotIn(
            '{} - {}'.format(testassignment2.long_name, testassignment2.parentnode.long_name),
            valuelist
        )
        self.assertIn(
            '{} - {}'.format(testassignment1.long_name, testassignment1.parentnode.long_name),
            valuelist
        )

    def test_multiple_assignments(self):
        testassignment1 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='cool',
            parentnode__short_name='asd',
            parentnode__long_name='Adfsad'
        )
        testassignment2 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_middle',
            short_name='cool',
            parentnode__short_name='ghdfg',
            parentnode__long_name='Oijjop',
            parentnode__parentnode=testassignment1.parentnode.parentnode
        )
        testassignment3 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_end',
            short_name='cool',
            parentnode__short_name='polmfhg',
            parentnode__long_name='KOPkop',
            parentnode__parentnode=testassignment1.parentnode.parentnode
        )
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='cool',
            parentnode__short_name='s17',
            parentnode__long_name='spring17',
            parentnode__parentnode=testassignment1.parentnode.parentnode
        )
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'period_id': testassignment1.parentnode.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        valuelist = [elem.alltext_normalized for elem in mockresponse.selector.list(
            '.django-cradmin-listbuilder-itemvalue-titledescription-title')]
        self.assertEqual(3, len(valuelist))
        self.assertNotIn(
            '{} - {}'.format(testassignment.long_name, testassignment.parentnode.long_name),
            valuelist
        )
        self.assertIn(
            '{} - {}'.format(testassignment1.long_name, testassignment1.parentnode.long_name),
            valuelist
        )
        self.assertIn(
            '{} - {}'.format(testassignment2.long_name, testassignment2.parentnode.long_name),
            valuelist
        )
        self.assertIn(
            '{} - {}'.format(testassignment3.long_name, testassignment3.parentnode.long_name),
            valuelist
        )

    def test_multiple_assignments_not_in(self):
        testassignment1 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='assignment1',
            parentnode__short_name='asd',
            parentnode__long_name='Adfsad'
        )
        testassignment2 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_middle',
            short_name='cool',
            parentnode__short_name='ghdfg',
            parentnode__long_name='Oijjop'
        )
        testassignment3 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_end',
            short_name='cool',
            parentnode__short_name='polmfhg',
            parentnode__long_name='KOPkop',
            parentnode__parentnode=testassignment1.parentnode.parentnode
        )
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='cool',
            parentnode__short_name='s17',
            parentnode__long_name='spring17',
            parentnode__parentnode=testassignment1.parentnode.parentnode
        )
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'period_id': testassignment1.parentnode.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        valuelist = [elem.alltext_normalized for elem in mockresponse.selector.list(
            '.django-cradmin-listbuilder-itemvalue-titledescription-title')]
        self.assertEqual(1, len(valuelist))
        self.assertNotIn(
            '{} - {}'.format(testassignment.long_name, testassignment.parentnode.long_name),
            valuelist
        )
        self.assertNotIn(
            '{} - {}'.format(testassignment1.long_name, testassignment1.parentnode.long_name),
            valuelist
        )
        self.assertNotIn(
            '{} - {}'.format(testassignment2.long_name, testassignment2.parentnode.long_name),
            valuelist
        )
        self.assertIn(
            '{} - {}'.format(testassignment3.long_name, testassignment3.parentnode.long_name),
            valuelist
        )

    def test_select_previous_period_multiple_future_not_in(self):
        testassignment1 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_middle',
            short_name='cool',
            parentnode__short_name='ghdfg',
            parentnode__long_name='Oijjop'
        )
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='cool',
            parentnode__short_name='s17',
            parentnode__long_name='spring17',
            parentnode__parentnode=testassignment1.parentnode.parentnode
        )
        testassignment2 = mommy.make_recipe(
            'devilry.apps.core.assignment_futureperiod_start',
            short_name='cool',
            parentnode__short_name='sdgf',
            parentnnode__long_name='opkjmdgf',
            parentnode__parentnode=testassignment1.parentnode.parentnode
        )
        testassignment3 = mommy.make_recipe(
            'devilry.apps.core.assignment_futureperiod_middle',
            short_name='cool',
            parentnode__short_name='hgdf',
            parentnnode__long_name='asdads',
            parentnode__parentnode=testassignment1.parentnode.parentnode
        )

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'period_id': testassignment1.parentnode.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        valuelist = [elem.alltext_normalized for elem in mockresponse.selector.list(
            '.django-cradmin-listbuilder-itemvalue-titledescription-title')]
        self.assertEqual(1, len(valuelist))
        self.assertNotIn(
            '{} - {}'.format(testassignment.long_name, testassignment.parentnode.long_name),
            valuelist
        )
        self.assertIn(
            '{} - {}'.format(testassignment1.long_name, testassignment1.parentnode.long_name),
            valuelist
        )
        self.assertNotIn(
            '{} - {}'.format(testassignment2.long_name, testassignment2.parentnode.long_name),
            valuelist
        )
        self.assertNotIn(
            '{} - {}'.format(testassignment3.long_name, testassignment3.parentnode.long_name),
            valuelist
        )


class TestApprovePreviousViewAnonymization(TestAssignmentViewAnonymization):
    viewclass = passed_previous_period.ApprovePreviousAssignments


class TestApprovePreviousView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = passed_previous_period.ApprovePreviousAssignments

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_title(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'period_id': testassignment.parentnode.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        self.assertIn(
            'Approve assignments',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'period_id': testassignment.parentnode.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        self.assertIn(
            'Step 3 of 3: Approve assignments for the following students.',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_confirm_button(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'period_id': testassignment.parentnode.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        self.assertIn(
            'Confirm',
            mockresponse.selector.one('#submit-id-confirm').alltext_normalized)

    def test_links(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'period_id': testassignment.parentnode.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )

        self.assertEquals(1, len(mockresponse.request.cradmin_instance.reverse_url.call_args_list))
        self.assertEqual(
            mock.call(appname='passed_previous_period', args=(),
                      kwargs={'period_id': testassignment.parentnode.id}, viewname='assignments'),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[0]
        )


class TestCandidateListbuilder(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = passed_previous_period.ApprovePreviousAssignments

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_simple_title(self):
        testassignment1 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='cool',
            parentnode__short_name='s16',
            parentnode__long_name='spring16',
            passing_grade_min_points=1,
            max_points=1,
        )
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment1)
        candidate1 = core_mommy.candidate(group=group1, shortname='april', fullname='April Duck')
        group_mommy.feedbackset_first_attempt_published(group=group1, grading_points=1)

        testassignment2 = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='cool',
            parentnode__parentnode=testassignment1.parentnode.parentnode,
            passing_grade_min_points=2,
            max_points=3,
        )
        group2 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)
        mommy.make('core.Candidate', assignment_group=group2, relatedstudent__user=candidate1.relatedstudent.user)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment2,
            viewkwargs={'period_id': testassignment1.parentnode.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )

        valuelist = [elem.alltext_normalized for elem in mockresponse.selector.list(
            '.django-cradmin-listbuilder-itemvalue-titledescription-title')]
        self.assertEqual(1, len(valuelist))
        self.assertIn(
            '{}({})'.format(candidate1.relatedstudent.user.fullname, candidate1.relatedstudent.user.shortname),
            valuelist
        )

    def test_simple_description(self):
        testassignment1 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='cool',
            parentnode__short_name='s16',
            parentnode__long_name='spring16',
            passing_grade_min_points=1,
            max_points=1,
        )
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment1)
        candidate1 = core_mommy.candidate(group=group1, shortname='april', fullname='April Duck')
        group_mommy.feedbackset_first_attempt_published(group=group1, grading_points=1)

        testassignment2 = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='cool',
            parentnode__parentnode=testassignment1.parentnode.parentnode,
            passing_grade_min_points=2,
            max_points=3,
        )
        group2 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)
        mommy.make('core.Candidate', assignment_group=group2, relatedstudent__user=candidate1.relatedstudent.user)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment2,
            viewkwargs={'period_id': testassignment1.parentnode.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )

        valuelist = [elem.alltext_normalized for elem in mockresponse.selector.list(
            '.django-cradmin-listbuilder-itemvalue-titledescription-description')]
        self.assertEqual(2, len(valuelist))
        self.assertIn('{} - {}'.format(testassignment1.long_name, testassignment1.parentnode.long_name), valuelist)
        self.assertIn('passed (1/1) passed (3/3)', valuelist)

    def test_multiple_title(self):
        testassignment1 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='cool',
            parentnode__short_name='s16',
            parentnode__long_name='spring16',
            passing_grade_min_points=1,
            max_points=1,
        )
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment1)
        candidate1 = core_mommy.candidate(group=group1, shortname='april', fullname='April Duck')
        group_mommy.feedbackset_first_attempt_published(group=group1, grading_points=1)

        group2 = mommy.make('core.AssignmentGroup', parentnode=testassignment1)
        candidate2 = core_mommy.candidate(group=group2, shortname='donald', fullname='Donald Duck')
        group_mommy.feedbackset_first_attempt_published(group=group2, grading_points=1)

        group3 = mommy.make('core.AssignmentGroup', parentnode=testassignment1)
        candidate3 = core_mommy.candidate(group=group3, shortname='dewey', fullname='Dewey Duck')
        group_mommy.feedbackset_first_attempt_published(group=group3, grading_points=1)

        testassignment2 = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='cool',
            parentnode__parentnode=testassignment1.parentnode.parentnode,
            passing_grade_min_points=2,
            max_points=3,
        )
        new_group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)
        mommy.make('core.Candidate', assignment_group=new_group1, relatedstudent__user=candidate1.relatedstudent.user)

        new_group2 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)
        mommy.make('core.Candidate', assignment_group=new_group2, relatedstudent__user=candidate2.relatedstudent.user)

        new_group3 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)
        mommy.make('core.Candidate', assignment_group=new_group3, relatedstudent__user=candidate3.relatedstudent.user)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment2,
            viewkwargs={'period_id': testassignment1.parentnode.id},
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )

        valuelist = [elem.alltext_normalized for elem in mockresponse.selector.list(
            '.django-cradmin-listbuilder-itemvalue-titledescription-title')]
        self.assertEqual(3, len(valuelist))
        self.assertIn(
            '{}({})'.format(candidate1.relatedstudent.user.fullname, candidate1.relatedstudent.user.shortname),
            valuelist
        )
        self.assertIn(
            '{}({})'.format(candidate2.relatedstudent.user.fullname, candidate2.relatedstudent.user.shortname),
            valuelist
        )
        self.assertIn(
            '{}({})'.format(candidate3.relatedstudent.user.fullname, candidate3.relatedstudent.user.shortname),
            valuelist
        )


class TestApprovePreviousPostView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = passed_previous_period.ApprovePreviousAssignments

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_no_candidates_passed(self):
        testassignment2 = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='cool',
            passing_grade_min_points=2,
            max_points=3,
        )
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testassignment2,
            viewkwargs={'period_id': testassignment2.parentnode.id},
            messagesmock=messagesmock,
            requestkwargs={
                'data': {
                    'candidates': '[]'
                }
            },
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        self.assertFalse(FeedbacksetPassedPreviousPeriod.objects.all().exists())
        messagesmock.add.assert_called_once_with(
            messages.WARNING,
            'No students are qualified to get approved for this assignment from a previous assignment.',
            ''
        )

    def test_success_simple(self):
        testassignment1 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='cool',
            parentnode__short_name='s16',
            parentnode__long_name='spring16',
            passing_grade_min_points=1,
            max_points=1,
        )
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment1)
        candidate1 = core_mommy.candidate(group=group1, shortname='april', fullname='April Duck')
        group_mommy.feedbackset_first_attempt_published(group=group1, grading_points=1)

        testassignment2 = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='cool',
            parentnode__parentnode=testassignment1.parentnode.parentnode,
            passing_grade_min_points=2,
            max_points=3,
        )
        group2 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)
        mommy.make('core.Candidate', assignment_group=group2, relatedstudent__user=candidate1.relatedstudent.user)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testassignment2,
            viewkwargs={'period_id': testassignment1.parentnode.id},
            messagesmock=messagesmock,
            requestkwargs={
                'data': {
                    'candidates': '[{}]'.format(candidate1.id)
                }
            },
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        feedbackset_passed_previous_period = FeedbacksetPassedPreviousPeriod.objects.get()
        self.assertEqual(feedbackset_passed_previous_period.passed_previous_period_type,
                         FeedbacksetPassedPreviousPeriod.PASSED_PREVIOUS_SEMESTER_TYPES.AUTO.value)
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            '{} was marked as approved for this assignment.'.format(candidate1.relatedstudent.user.get_displayname()),
            ''
        )

    def test_success_multiple(self):
        testassignment1 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='cool',
            passing_grade_min_points=1,
            max_points=1,
        )
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment1)
        candidate1 = core_mommy.candidate(group=group1, shortname='april', fullname='April Duck')
        group_mommy.feedbackset_first_attempt_published(group=group1, grading_points=1)

        group2 = mommy.make('core.AssignmentGroup', parentnode=testassignment1)
        candidate2 = core_mommy.candidate(group=group2, shortname='donald', fullname='Donald Duck')
        group_mommy.feedbackset_first_attempt_published(group=group2, grading_points=1)

        testassignment0 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_middle',
            short_name='cool',
            parentnode__parentnode=testassignment1.parentnode.parentnode,
            passing_grade_min_points=1,
            max_points=1,
        )

        group3 = mommy.make('core.AssignmentGroup', parentnode=testassignment0)
        candidate3 = core_mommy.candidate(group=group3, shortname='dewey', fullname='Dewey Duck')
        group_mommy.feedbackset_first_attempt_published(group=group3, grading_points=1)

        testassignment2 = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='cool',
            parentnode__parentnode=testassignment1.parentnode.parentnode,
            passing_grade_min_points=2,
            max_points=3,
        )
        new_group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)
        mommy.make('core.Candidate', assignment_group=new_group1, relatedstudent__user=candidate1.relatedstudent.user)

        new_group2 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)
        mommy.make('core.Candidate', assignment_group=new_group2, relatedstudent__user=candidate2.relatedstudent.user)

        new_group3 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)
        mommy.make('core.Candidate', assignment_group=new_group3, relatedstudent__user=candidate3.relatedstudent.user)

        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testassignment2,
            viewkwargs={'period_id': testassignment1.parentnode.id},
            messagesmock=messagesmock,
            requestkwargs={
                'data': {
                    'candidates': '[{}, {}, {}]'.format(candidate1.id, candidate2.id, candidate3.id)
                }
            },
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            '{}, {}, {} was marked as approved for this assignment.'
            ''.format(candidate1.relatedstudent.user.get_displayname(),
                      candidate2.relatedstudent.user.get_displayname(),
                      candidate3.relatedstudent.user.get_displayname()),
            ''
        )

    def test_warning_some_candidates_does_not_qualify(self):
        testassignment1 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='cool',
            passing_grade_min_points=1,
            max_points=1,
        )
        group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment1)
        candidate1 = core_mommy.candidate(group=group1, shortname='april', fullname='April Duck')
        group_mommy.feedbackset_first_attempt_published(group=group1, grading_points=1)

        group2 = mommy.make('core.AssignmentGroup', parentnode=testassignment1)
        candidate2 = core_mommy.candidate(group=group2, shortname='donald', fullname='Donald Duck')
        group_mommy.feedbackset_first_attempt_published(group=group2, grading_points=1)

        testassignment0 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_middle',
            short_name='imba',
            parentnode__parentnode=testassignment1.parentnode.parentnode,
            passing_grade_min_points=1,
            max_points=1,
        )

        group3 = mommy.make('core.AssignmentGroup', parentnode=testassignment0)
        candidate3 = core_mommy.candidate(group=group3, shortname='dewey', fullname='Dewey Duck')
        group_mommy.feedbackset_first_attempt_published(group=group3, grading_points=1)

        testassignment2 = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='cool',
            parentnode__parentnode=testassignment1.parentnode.parentnode,
            passing_grade_min_points=2,
            max_points=3,
        )
        new_group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)
        mommy.make('core.Candidate', assignment_group=new_group1, relatedstudent__user=candidate1.relatedstudent.user)

        new_group2 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)
        mommy.make('core.Candidate', assignment_group=new_group2, relatedstudent__user=candidate2.relatedstudent.user)

        new_group3 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)
        mommy.make('core.Candidate', assignment_group=new_group3, relatedstudent__user=candidate3.relatedstudent.user)

        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=testassignment2,
            viewkwargs={'period_id': testassignment1.parentnode.id},
            messagesmock=messagesmock,
            requestkwargs={
                'data': {
                    'candidates': '[{}, {}, {}]'.format(candidate1.id, candidate2.id, candidate3.id)
                }
            },
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        messagesmock.add.assert_called_once_with(
            messages.WARNING,
            'Some students does not qualify to pass the assignment.',
            ''
        )
