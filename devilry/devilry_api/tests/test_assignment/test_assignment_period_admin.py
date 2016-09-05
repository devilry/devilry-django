from model_mommy import mommy
from rest_framework.test import APITestCase

from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from devilry.devilry_api import devilry_api_mommy_factories as api_mommy
from devilry.devilry_api.assignment.views import assignment_period_admin
from devilry.devilry_api.tests.mixins import test_period_admin_mixins, api_test_helper, test_common_mixins
from devilry.devilry_api.tests.mixins.test_common_filters_mixin import TestAssignmentFiltersPeriodAdminMixin


class TestPeriodAdminAssignmentview(test_common_mixins.TestReadOnlyPermissionMixin,
                                    test_period_admin_mixins.TestAuthAPIKeyPeriodAdminMixin,
                                    api_test_helper.TestCaseMixin,
                                    APITestCase):
    viewclass = assignment_period_admin.PeriodAdminAssignmentView

    def test_unauthorized_401(self):
        response = self.mock_get_request()
        self.assertEqual(401, response.status_code)

    def test_sanity(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 1)

    def test_id(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', id=10)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(10, response.data[0]['id'])

    def test_long_name(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', long_name='Assignment 1')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual('Assignment 1', response.data[0]['long_name'])

    def test_short_name(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', short_name='assignment0')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual('assignment0', response.data[0]['short_name'])

    def test_period_short_name(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', parentnode__short_name='V15')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual('V15', response.data[0]['period_short_name'])

    def test_subject_short_name(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       parentnode__parentnode__short_name='Duck1010')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual('Duck1010', response.data[0]['subject_short_name'])

    def test_publishing_time(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.publishing_time.isoformat(), response.data[0]['publishing_time'])

    def test_anonymizationmode(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.anonymizationmode, response.data[0]['anonymizationmode'])

    def test_num_queries(self):
        period = mommy.make('core.Period')
        for x in range(10):
            mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', parentnode=period)
        period_admin = core_mommy.period_admin(period=period)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        with self.assertNumQueries(2):
            self.mock_get_request(apikey=apikey.key)


class TestPeriodAdminAssignmentViewFilters(api_test_helper.TestCaseMixin,
                                           TestAssignmentFiltersPeriodAdminMixin,
                                           APITestCase):
    viewclass = assignment_period_admin.PeriodAdminAssignmentView

    def test_filter_search_short_name_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       short_name='assignment1')
        period_admin = core_mommy.period_admin(assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=assignment0')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_search_short_name_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       short_name='assignment1')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=assignment1')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.short_name, response.data[0]['short_name'])

    def test_filter_short_name_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       short_name='assignment1')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?short_name=assignment0')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_short_name_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       short_name='assignment1')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?short_name=assignment1')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.short_name, response.data[0]['short_name'])

    def test_filter_id_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', id=55)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?id=3')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_id_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', id=55)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?id=55')
        self.assertEqual(200, response.status_code)
        self.assertEqual(55, response.data[0]['id'])

    def test_ordering_short_name_asc(self):
        period = mommy.make('core.Period')
        assignment1 = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                        short_name='AAA', parentnode=period)
        assignment2 = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                        short_name='BBB', parentnode=period)
        period_admin = core_mommy.period_admin(period=period)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?ordering=short_name')
        self.assertEqual(200, response.status_code)
        assignment_publishing_time = [assignment['short_name'] for assignment in response.data]
        self.assertListEqual([assignment1.short_name,
                              assignment2.short_name], assignment_publishing_time)

    def test_ordering_short_name_desc(self):
        period = mommy.make('core.Period')
        assignment1 = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                        short_name='AAA', parentnode=period)
        assignment2 = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                        short_name='BBB', parentnode=period)
        period_admin = core_mommy.period_admin(period=period)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?ordering=-short_name')
        self.assertEqual(200, response.status_code)
        assignment_publishing_time = [assignment['short_name'] for assignment in response.data]
        self.assertListEqual([assignment2.short_name,
                              assignment1.short_name], assignment_publishing_time)
