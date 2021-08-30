from django.test import TestCase
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker
from django.utils import timezone

from devilry.devilry_admin.views.assignment import first_deadline
from devilry.utils.datetimeutils import default_timezone_datetime
from django.template import defaultfilters


class TestOverviewAppUpdateFirstDeadline(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = first_deadline.AssignmentFirstDeadlineUpdateView

    def test_h1(self):
        assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment, viewkwargs={'pk':assignment.id})
        self.assertEqual(mockresponse.selector.one('h1').alltext_normalized, 'Edit first deadline')

    def test_update_first_deadline_sanity(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        new_first_deadline = default_timezone_datetime(3000, 12, 31, 23, 59)
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            viewkwargs={
                'pk': testassignment.id
            },
            requestkwargs={
                'data': {
                    'first_deadline': new_first_deadline
                }
            })
        testassignment.refresh_from_db()
        self.assertEqual(
            new_first_deadline.replace(second=59),
            testassignment.first_deadline
        )
    
    def test_update_first_deadline_before_period_start_error_sanity(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        orginal_first_deadline = testassignment.first_deadline
        new_first_deadline = testperiod.start_time - timezone.timedelta(days=1)
        mockresponse =self.mock_http200_postrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={
                'pk': testassignment.id
            },
            requestkwargs={
                'data': {
                    'first_deadline': new_first_deadline
                }
            })
        self.assertIn(
            f'First deadline must be within {testperiod.long_name}, which lasts from ', 
            mockresponse.selector.one('#error_1_id_first_deadline').alltext_normalized
        )
        testassignment.refresh_from_db()
        self.assertEqual(
            testassignment.first_deadline,
            orginal_first_deadline,
        )
    
    def test_update_first_deadline_after_period_end_error_sanity(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        orginal_first_deadline = testassignment.first_deadline
        new_first_deadline = testperiod.end_time + timezone.timedelta(days=1)
        mockresponse =self.mock_http200_postrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={
                'pk': testassignment.id
            },
            requestkwargs={
                'data': {
                    'first_deadline': new_first_deadline
                }
            })
        self.assertIn(
            f'First deadline must be within {testperiod.long_name}, which lasts from ', 
            mockresponse.selector.one('#error_1_id_first_deadline').alltext_normalized
        )
        testassignment.refresh_from_db()
        self.assertEqual(
            testassignment.first_deadline,
            orginal_first_deadline,
        )
