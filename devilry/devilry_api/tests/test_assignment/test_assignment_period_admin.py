from model_mommy import mommy
from rest_framework.test import APITestCase

from devilry.apps.core.models import Assignment
from devilry.apps.core import mommy_recipes as core_recipes
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

    def test_period_admin_not_part_of_permission_group(self):
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', id=10)
        period_admin = core_mommy.period_admin(period=mommy.make('core.Period'))
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?id=10')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_period_admin_old_period(self):
        assingment = mommy.make_recipe('devilry.apps.core.assignment_oldperiod_start', id=10)
        period_admin = core_mommy.period_admin(period=assingment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?id=10')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_period_admin_future_period(self):
        assingment = mommy.make_recipe('devilry.apps.core.assignment_futureperiod_start', id=10)
        period_admin = core_mommy.period_admin(period=assingment.parentnode)
        apikey = api_mommy.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key, queryparams='?id=10')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

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


class TestPeriodAdminAssignmentViewPost(api_test_helper.TestCaseMixin,
                                        APITestCase):
    viewclass = assignment_period_admin.PeriodAdminAssignmentView

    def test_unauthorized_401(self):
        response = self.mock_post_request()
        self.assertEqual(401, response.status_code)

    def test_not_part_of_period(self):
        mommy.make('core.Period', id=11)
        period_admin = core_mommy.period_admin(period=mommy.make('core.Period'))
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_post_request(apikey=apikey.key, data={
            'period_id': 10,
            'short_name': 'assignment1',
            'long_name': 'The best assignment',
            'publishing_time': core_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_PUBLISHING_TIME
        })
        self.assertEqual(403, response.status_code)
        self.assertEqual('Access denied Period admin not part of period.', response.data['detail'])

    def test_period_id_missing(self):
        period_admin = core_mommy.period_admin(period=mommy.make('core.Period', id=10))
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_post_request(apikey=apikey.key, data={
            'short_name': 'assignment1',
            'long_name': 'The best assignment',
            'publishing_time': core_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_PUBLISHING_TIME
        })
        self.assertEqual(400, response.status_code)
        self.assertEqual(['This field is required.'], response.data['period_id'])

    def test_short_name_missing(self):
        period_admin = core_mommy.period_admin(period=mommy.make('core.Period', id=10))
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_post_request(apikey=apikey.key, data={
            'period_id': 10,
            'long_name': 'The best assignment',
            'publishing_time': core_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_PUBLISHING_TIME
        })
        self.assertEqual(400, response.status_code)
        self.assertEqual(['This field is required.'], response.data['short_name'])

    def test_long_name_missing(self):
        period_admin = core_mommy.period_admin(period=mommy.make('core.Period', id=10))
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_post_request(apikey=apikey.key, data={
            'period_id': 10,
            'short_name': 'assignment1',
            'publishing_time': core_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_PUBLISHING_TIME
        })
        self.assertEqual(400, response.status_code)
        self.assertEqual(['This field is required.'], response.data['long_name'])

    def test_publishing_time_missing(self):
        period_admin = core_mommy.period_admin(period=mommy.make('core.Period', id=10))
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_post_request(apikey=apikey.key, data={
            'period_id': 10,
            'short_name': 'assignment1',
            'long_name': 'The best assignment',
        })
        self.assertEqual(400, response.status_code)
        self.assertEqual(['This field is required.'], response.data['publishing_time'])

    def test_post_assignment_sanity(self):
        period_admin = core_mommy.period_admin(period=mommy.make('core.Period', id=10,
                                                                 short_name='spriiiiing',
                                                                 parentnode__short_name='duck1010'))
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_post_request(apikey=apikey.key, data={
            'period_id': 10,
            'short_name': 'assignment1',
            'long_name': 'The best assignment',
            'publishing_time': core_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_PUBLISHING_TIME
        })
        self.assertEqual(201, response.status_code)
        self.assertEqual(response.data['anonymizationmode'], Assignment.ANONYMIZATIONMODE_OFF)
        self.assertEqual(response.data['short_name'], 'assignment1')
        self.assertEqual(response.data['long_name'], 'The best assignment')
        self.assertEqual(response.data['publishing_time'],
                         core_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_PUBLISHING_TIME.isoformat())
        self.assertEqual(response.data['period_id'], 10)
        self.assertEqual(response.data['period_short_name'], 'spriiiiing')
        self.assertEqual(response.data['subject_short_name'], 'duck1010')

    def test_post_assignment_created_in_db(self):
        period_admin = core_mommy.period_admin(period=mommy.make('core.Period', id=10))
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_post_request(apikey=apikey.key, data={
            'period_id': 10,
            'short_name': 'assignment1',
            'long_name': 'The best assignment',
            'publishing_time': core_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_PUBLISHING_TIME
        })
        self.assertEqual(201, response.status_code)
        assignment = Assignment.objects.get(id=response.data['id'])
        self.assertEqual(response.data['period_id'], assignment.parentnode.id)
        self.assertEqual(response.data['id'], assignment.id)
        self.assertEqual(response.data['short_name'], assignment.short_name)
        self.assertEqual(response.data['long_name'], assignment.long_name)
        self.assertEqual(response.data['publishing_time'], assignment.publishing_time.isoformat())
        self.assertEqual(response.data['anonymizationmode'], assignment.anonymizationmode)
        self.assertEqual(response.data['period_short_name'], assignment.parentnode.short_name)
        self.assertEqual(response.data['subject_short_name'], assignment.parentnode.parentnode.short_name)
