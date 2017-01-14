from model_mommy import mommy
from rest_framework.test import APITestCase

from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core import mommy_recipes as core_recipes
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from devilry.devilry_api import devilry_api_mommy_factories as api_mommy
from devilry.apps.core.models.assignment import Assignment
from devilry.devilry_api.assignment_group.views.assignmentgroup_period_admin import AssignmentGroupViewPeriodAdmin
from devilry.devilry_api.tests.mixins import test_admin_mixins, api_test_helper, test_common_mixins
from devilry.devilry_api.tests.mixins.test_common_filters_mixin import TestAssignmentFiltersPeriodAdminMixin


class TestPeriodAdminAssignmentgroupView(test_common_mixins.TestReadOnlyPermissionMixin,
                                         test_admin_mixins.TestAuthAPIKeyAdminMixin,
                                         api_test_helper.TestCaseMixin,
                                         APITestCase):
    viewclass = AssignmentGroupViewPeriodAdmin

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

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

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

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
        group = mommy.make('core.AssignmentGroup', parentnode=assignment, id=1337)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?id=1337')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['id'], group.id)

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


# class TestPeriodAdminAssignmentGroupPost(api_test_helper.TestCaseMixin,
#                                          APITestCase):
#     viewclass = AssignmentGroupViewPeriodAdmin
#
#     def test_unauthorized_401(self):
#         response = self.mock_post_request()
#         self.assertEqual(response.status_code, 401)
#
#     def test_not_part_of_period(self):
#         mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', id=1337)
#         period_admin = core_mommy.period_admin(period=mommy.make('core.Period'))
#         apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
#         response = self.mock_post_request(
#             apikey=apikey.key,
#             data={
#                 'assignment_id': 1337,
#                 'name': 'Cool group'
#             })
#         self.assertEqual(response.data['detail'], 'Permission denied: not part of period')
#         self.assertEqual(response.status_code, 403)
#
#     def test_assignment_id_missing(self):
#         assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', id=1337)
#         period_admin = core_mommy.period_admin(period=assignment.parentnode)
#         apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
#         response = self.mock_post_request(
#             apikey=apikey.key,
#             data={
#                 'name': 'Cool group'
#             })
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.data['assignment_id'], ['This field is required.'])
#
#     def test_created_in_db(self):
#         assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', id=1337)
#         period_admin = core_mommy.period_admin(period=assignment.parentnode)
#         apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
#         response = self.mock_post_request(
#             apikey=apikey.key,
#             data={
#                 'assignment_id': 1337,
#                 'name': 'Cool group'
#             })
#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(response.data['name'], 'Cool group')
#         group = AssignmentGroup.objects.filter(parentnode__id=1337).first()
#         self.assertIsNotNone(group)
#         self.assertEqual(group.name, 'Cool group')


class TestPeriodAdminDelete(api_test_helper.TestCaseMixin,
                            APITestCase):
    viewclass = AssignmentGroupViewPeriodAdmin

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_unauthorized_401(self):
        response = self.mock_delete_request()
        self.assertEqual(response.status_code, 401)

    def test_delete_anonymization_semi_anonymous(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.AssignmentGroup', parentnode=assignment, id=1337)
        period_admin = core_mommy.period_admin(period=mommy.make('core.Period'))
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_delete_request(
            apikey=apikey.key,
            queryparams='?id=1337'
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], 'Assignment group with id: 1337 not found.')

    def test_delete_anonymization_fully_anonymous(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        mommy.make('core.AssignmentGroup', parentnode=assignment, id=1337)
        period_admin = core_mommy.period_admin(period=mommy.make('core.Period'))
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_delete_request(
            apikey=apikey.key,
            queryparams='?id=1337'
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], 'Assignment group with id: 1337 not found.')

    def test_delete_not_in_period(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mommy.make('core.AssignmentGroup', parentnode=assignment, id=1337)
        period_admin = core_mommy.period_admin(period=mommy.make('core.Period'))
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_delete_request(
            apikey=apikey.key,
            queryparams='?id=1337'
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], 'Assignment group with id: 1337 not found.')

    def test_not_allowed_to_delete(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment, id=1337)
        core_mommy.candidate(group)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_delete_request(
            apikey=apikey.key,
            queryparams='?id=1337'
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], 'Permission denied: cannot delete assignment group.')
        group_db = AssignmentGroup.objects.filter(id=1337).first()
        self.assertIsNotNone(group_db)

    def test_delete_in_db(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mommy.make('core.AssignmentGroup', parentnode=assignment, id=1337)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_delete_request(
            apikey=apikey.key,
            queryparams='?id=1337'
        )
        self.assertEqual(response.status_code, 204)
        group = AssignmentGroup.objects.filter(id=1337).first()
        self.assertIsNone(group)
