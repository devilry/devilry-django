from model_mommy import mommy
from rest_framework.test import APITestCase

from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from devilry.devilry_api import devilry_api_mommy_factories as api_mommy
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_api.tests.mixins import test_period_admin_mixins, api_test_helper, test_common_mixins
from devilry.devilry_api.feedbackset.views.feedbackset_period_admin import FeedbacksetViewPeriodAdmin
from devilry.devilry_group.models import FeedbackSet
from devilry.apps.core.models import Assignment


class TestFeedbacksetSanity(test_common_mixins.TestReadOnlyPermissionMixin,
                            test_period_admin_mixins.TestAuthAPIKeyPeriodAdminMixin,
                            api_test_helper.TestCaseMixin,
                            APITestCase):
    viewclass = FeedbacksetViewPeriodAdmin

    def test_unauthorized_401(self):
        response = self.mock_get_request()
        self.assertEqual(401, response.status_code)

    def test_anonymization_mode_semi_anonymous_no_access(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        mommy.make('devilry_group.Feedbackset', group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 0)

    def test_anonymization_mode_fully_anonymous_no_access(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        mommy.make('devilry_group.Feedbackset', group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 0)

    def test_sanity(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        mommy.make('devilry_group.Feedbackset', group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 1)

    def test_group_id(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        mommy.make('devilry_group.Feedbackset', group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['group_id'], group.id)

    def test_created_datetime(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = mommy.make('devilry_group.Feedbackset', group=group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['created_datetime'], feedbackset.created_datetime.isoformat())

    def test_is_last_in_group(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = mommy.make('devilry_group.Feedbackset',
                                 group=group,
                                 is_last_in_group=True)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['is_last_in_group'], feedbackset.is_last_in_group)

    def test_deadline_datetime_first_attempt(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        mommy.make('devilry_group.Feedbackset',
                   group=group,
                   feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['deadline_datetime'], group.parentnode.first_deadline.isoformat())

    def test_deadline_datetime_new_attempt(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        feedbackset = mommy.make('devilry_group.Feedbackset',
                                 group=group,
                                 feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['deadline_datetime'], feedbackset.deadline_datetime)

