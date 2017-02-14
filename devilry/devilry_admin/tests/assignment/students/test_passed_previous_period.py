import mock
from django.contrib import messages
from django.http import Http404
from django.test import TestCase
from django.conf import settings
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from devilry.apps.core.models import AssignmentGroup, Candidate, Assignment
from devilry.devilry_admin.views.assignment.students import passed_previous_period
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


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

    def test_submit_button_text(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin')
        )
        self.assertIn(
            'Next',
            mockresponse.selector.one('#submit-id-next').alltext_normalized)

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
        selectlist = [elem.alltext_normalized for elem in mockresponse.selector.list('.controls  > .radio')]
        self.assertEqual(2, len(selectlist))
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
        selectlist = [elem.alltext_normalized for elem in mockresponse.selector.list('.controls  > .radio')]
        self.assertEqual(4, len(selectlist))
        self.assertNotIn(
            '{} - {}'.format(testassignment.parentnode.short_name, testassignment.parentnode.long_name),
            selectlist
        )
        self.assertIn(
            '{} - {}'.format(period1.short_name, period1.long_name),
            selectlist
        )
        self.assertIn(
            '{} - {}'.format(period2.short_name, period2.long_name),
            selectlist
        )
        self.assertIn(
            '{} - {}'.format(period3.short_name, period3.long_name),
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
        selectlist = [elem.alltext_normalized for elem in mockresponse.selector.list('.controls  > .radio')]
        self.assertEqual(2, len(selectlist))
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
        selectlist = [elem.alltext_normalized for elem in mockresponse.selector.list('.controls  > .radio')]
        self.assertEqual(2, len(selectlist))
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
            mock.call(appname='overview', args=(), kwargs={}, viewname='INDEX'),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[0]
        )
