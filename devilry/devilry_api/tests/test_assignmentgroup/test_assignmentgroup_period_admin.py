from model_mommy import mommy
from rest_framework.test import APITestCase

from devilry.apps.core import mommy_recipes as core_recipes
from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from devilry.devilry_api import devilry_api_mommy_factories as api_mommy
from devilry.apps.core.models.assignment import Assignment
from devilry.devilry_api.assignment_group.views.assignmentgroup_period_admin import AssignmentGroupViewPeriodAdmin
from devilry.devilry_api.tests.mixins import test_period_admin_mixins, api_test_helper, test_common_mixins
from devilry.devilry_api.tests.mixins.test_common_filters_mixin import TestAssignmentFiltersPeriodAdminMixin


class TestPeriodAdminAssignmentgroupView(test_common_mixins.TestReadOnlyPermissionMixin,
                                         test_period_admin_mixins.TestAuthAPIKeyPeriodAdminMixin,
                                         api_test_helper.TestCaseMixin,
                                         APITestCase):
    viewclass = AssignmentGroupViewPeriodAdmin

    def test_unauthorized_401(self):
        response = self.mock_get_request()
        self.assertEqual(401, response.status_code)

    def test_anonymizationmode_semi_anonymous_no_access(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('core.AssignmentGroup', parentnode=assignment)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 0)

    def test_anonymizationmode_fully_anonymous_no_access(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('core.AssignmentGroup', parentnode=assignment)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 0)

    def test_sanity(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('core.AssignmentGroup', parentnode=assignment)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 1)

    def test_assignment_group_old(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_oldperiod_start')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('core.AssignmentGroup', parentnode=assignment)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 1)

    def test_assignment_group_future(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_futureperiod_start')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('core.AssignmentGroup', parentnode=assignment)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 1)

    def test_id(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('core.AssignmentGroup', parentnode=assignment, id=1337)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], 1337)

    def test_name(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('core.AssignmentGroup', parentnode=assignment, name='CoolGroup')
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['name'], 'CoolGroup')

    def test_assignment_id(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', id=1337)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('core.AssignmentGroup', parentnode=assignment)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['assignment_id'], 1337)

    def test_assignment_short_name(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', short_name='CoolAssignment')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('core.AssignmentGroup', parentnode=assignment)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['assignment_short_name'], 'CoolAssignment')

    def test_subject_short_name(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       parentnode__parentnode__short_name='CoolSubject')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('core.AssignmentGroup', parentnode=assignment)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['subject_short_name'], 'CoolSubject')

    def test_period_short_name(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       parentnode__short_name='ImbaPeriod')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('core.AssignmentGroup', parentnode=assignment)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['period_short_name'], 'ImbaPeriod')

    def test_short_displayname(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['short_displayname'], group.short_displayname)

    def test_long_displayname(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment, id=1337)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['long_displayname'], group.long_displayname)

    def test_num_queries(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        for x in range(10):
            mommy.make('core.AssignmentGroup', parentnode=assignment)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        with self.assertNumQueries(4):
            self.mock_get_request(apikey=apikey.key)


class TestPeriodAdminAssignmentViewFilters(api_test_helper.TestCaseMixin,
                                           TestAssignmentFiltersPeriodAdminMixin,
                                           APITestCase):
    viewclass = AssignmentGroupViewPeriodAdmin

    def test_filter_search_assignment_short_name_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       short_name='assignment1')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('core.AssignmentGroup', parentnode=assignment, id=1337)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=assignment0')
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 0)

    def test_filter_search_assignment_short_name_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       short_name='assignment1')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('core.AssignmentGroup', parentnode=assignment, id=1337)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=assignment1')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['assignment_short_name'], assignment.short_name)

    def test_filter_assignment_short_name_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       short_name='assignment1')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('core.AssignmentGroup', parentnode=assignment, id=1337)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?assignment_short_name=assignment0')
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 0)

    def test_filter_assignment_short_name_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       short_name='assignment1')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('core.AssignmentGroup', parentnode=assignment, id=1337)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?assignment_short_name=assignment1')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['assignment_short_name'], assignment.short_name)

    def test_filter_assignment_id_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       id=1338)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('core.AssignmentGroup', parentnode=assignment)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?assignment_id=1337')
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 0)

    def test_filter_assignment_id_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       id=1337)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('core.AssignmentGroup', parentnode=assignment)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?assignment_id=1337')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['assignment_id'], assignment.id)

    def test_filter_id_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('core.AssignmentGroup', parentnode=assignment, id=1337)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?id=1338')
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.data), 0)

    def test_filter_id_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('core.AssignmentGroup', parentnode=assignment, id=1337)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?id=1337')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], assignment.id)

    def test_ordering_name_asc(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('core.AssignmentGroup', parentnode=assignment, name='AAA')
        mommy.make('core.AssignmentGroup', parentnode=assignment, name='BBB')
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?ordering=name')
        self.assertEqual(200, response.status_code)
        self.assertListEqual(['AAA', 'BBB'], [group['name'] for group in response.data])

    def test_ordering_name_desc(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        mommy.make('core.AssignmentGroup', parentnode=assignment, name='AAA')
        mommy.make('core.AssignmentGroup', parentnode=assignment, name='BBB')
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?ordering=-name')
        self.assertEqual(200, response.status_code)
        self.assertListEqual(['BBB', 'AAA'], [group['name'] for group in response.data])
