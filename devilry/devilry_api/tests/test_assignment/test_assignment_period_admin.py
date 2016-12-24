from model_mommy import mommy
from rest_framework.test import APITestCase

from devilry.apps.core.models.assignment import Assignment
from devilry.apps.core.models import deliverytypes
from devilry.apps.core import mommy_recipes as core_recipes
from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from devilry.devilry_api import devilry_api_mommy_factories as api_mommy
from devilry.devilry_api.assignment.views import assignment_period_admin
from devilry.devilry_api.tests.mixins import test_admin_mixins, api_test_helper, test_common_mixins
from devilry.devilry_api.tests.mixins.test_common_filters_mixin import TestAssignmentFiltersPeriodAdminMixin


class TestPeriodAdminAssignmentview(test_common_mixins.TestReadOnlyPermissionMixin,
                                    test_admin_mixins.TestAuthAPIKeyAdminMixin,
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


class TestPeriodAdminAssignmentViewPatch(api_test_helper.TestCaseMixin,
                                         APITestCase):
    viewclass = assignment_period_admin.PeriodAdminAssignmentView

    def test_unauthorized_401(self):
        response = self.mock_patch_request()
        self.assertEqual(401, response.status_code)

    def test_patch_not_part_of_period(self):
        mommy.make('core.Assignment', id=11, parentnode=mommy.make('core.Period'))
        period_admin = core_mommy.period_admin(period=mommy.make('core.Period'))
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_patch_request(apikey=apikey.key, queryparams='?id=11', data={
            'short_name': 'assignment1',
            'long_name': 'The best assignment',
            'publishing_time': core_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_PUBLISHING_TIME
        })
        self.assertEqual(403, response.status_code)

    def test_patch_not_allowed_to_change_anything_semi_anonymous(self):
        period = mommy.make('core.Period')
        mommy.make('core.Assignment', id=11, parentnode=period,
                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        period_admin = core_mommy.period_admin(period=period)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_patch_request(apikey=apikey.key, data={
            'anonymizationmode': Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS
        }, queryparams='?id=11')
        self.assertEqual(403, response.status_code)

    def test_patch_not_allowed_to_change_anything_fully_anonymoyus(self):
        period = mommy.make('core.Period')
        mommy.make('core.Assignment', id=11, parentnode=period,
                   anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        period_admin = core_mommy.period_admin(period=period)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_patch_request(apikey=apikey.key, data={
            'anonymizationmode': Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS
        }, queryparams='?id=11')
        self.assertEqual(403, response.status_code)

    def test_patch_not_allowed_to_change_anonymization_mode(self):
        period = mommy.make('core.Period')
        mommy.make('core.Assignment', id=11, parentnode=period,
                   anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        period_admin = core_mommy.period_admin(period=period)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_patch_request(apikey=apikey.key, data={
            'anonymizationmode': Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS
        }, queryparams='?id=11')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['anonymizationmode'], Assignment.ANONYMIZATIONMODE_OFF)

    def test_patch_short_name(self):
        period = mommy.make('core.Period')
        mommy.make('core.Assignment', id=11, parentnode=period, short_name='Cool')
        period_admin = core_mommy.period_admin(period=period)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_patch_request(apikey=apikey.key, data={
            'short_name': 'assignment1'
        }, queryparams='?id=11')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['short_name'], 'assignment1')

    def test_patch_long_name(self):
        period = mommy.make('core.Period')
        mommy.make('core.Assignment', id=11, parentnode=period, long_name='Cool')
        period_admin = core_mommy.period_admin(period=period)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_patch_request(apikey=apikey.key, data={
            'long_name': 'Assignment 1'
        }, queryparams='?id=11')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['long_name'], 'Assignment 1')

    def test_patch_publishing_time(self):
        period = mommy.make('core.Period')
        mommy.make('core.Assignment', id=11, parentnode=period,
                   publishing_time=core_recipes.ASSIGNMENT_ACTIVEPERIOD_START_FIRST_DEADLINE)
        period_admin = core_mommy.period_admin(period=period)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_patch_request(apikey=apikey.key, data={
            'publishing_time': core_recipes.ASSIGNMENT_ACTIVEPERIOD_END_PUBLISHING_TIME
        }, queryparams='?id=11')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['publishing_time'],
                         core_recipes.ASSIGNMENT_ACTIVEPERIOD_END_PUBLISHING_TIME.isoformat())

    def test_patch_students_can_see_points(self):
        period = mommy.make('core.Period')
        mommy.make('core.Assignment', id=11, parentnode=period, students_can_see_points=False)
        period_admin = core_mommy.period_admin(period=period)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_patch_request(apikey=apikey.key, data={
            'students_can_see_points': True
        }, queryparams='?id=11')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['students_can_see_points'], True)

    def test_patch_delivery_types(self):
        period = mommy.make('core.Period')
        mommy.make('core.Assignment', id=11, parentnode=period,
                   delivery_types=deliverytypes.NON_ELECTRONIC)
        period_admin = core_mommy.period_admin(period=period)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_patch_request(apikey=apikey.key, data={
            'delivery_types': deliverytypes.ELECTRONIC
        }, queryparams='?id=11')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['delivery_types'], deliverytypes.ELECTRONIC)

    def test_patch_deadline_handling(self):
        period = mommy.make('core.Period')
        mommy.make('core.Assignment', id=11, parentnode=period,
                   deadline_handling=0)
        period_admin = core_mommy.period_admin(period=period)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_patch_request(apikey=apikey.key, data={
            'deadline_handling': 1
        }, queryparams='?id=11')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['deadline_handling'], 1)

    def test_patch_scale_points_percent(self):
        period = mommy.make('core.Period')
        mommy.make('core.Assignment', id=11, parentnode=period,
                   scale_points_percent=100)
        period_admin = core_mommy.period_admin(period=period)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_patch_request(apikey=apikey.key, data={
            'scale_points_percent': 50
        }, queryparams='?id=11')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['scale_points_percent'], 50)

    def test_patch_first_deadline(self):
        period = mommy.make('core.Period')
        mommy.make('core.Assignment', id=11, parentnode=period,
                   first_deadline=core_recipes.ASSIGNMENT_ACTIVEPERIOD_START_FIRST_DEADLINE)
        period_admin = core_mommy.period_admin(period=period)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_patch_request(apikey=apikey.key, data={
            'first_deadline': core_recipes.ASSIGNMENT_ACTIVEPERIOD_END_PUBLISHING_TIME
        }, queryparams='?id=11')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['first_deadline'],
                         core_recipes.ASSIGNMENT_ACTIVEPERIOD_END_PUBLISHING_TIME.isoformat())

    def test_patch_max_points(self):
        period = mommy.make('core.Period')
        mommy.make('core.Assignment', id=11, parentnode=period,
                   max_points=1)
        period_admin = core_mommy.period_admin(period=period)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_patch_request(apikey=apikey.key, data={
            'max_points': 101
        }, queryparams='?id=11')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['max_points'], 101)

    def test_patch_passing_grade_min_points(self):
        period = mommy.make('core.Period')
        mommy.make('core.Assignment', id=11, parentnode=period,
                   passing_grade_min_points=1)
        period_admin = core_mommy.period_admin(period=period)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_patch_request(apikey=apikey.key, data={
            'passing_grade_min_points': 101
        }, queryparams='?id=11')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['passing_grade_min_points'], 101)

    def test_patch_grading_system_plugin_id(self):
        period = mommy.make('core.Period')
        mommy.make('core.Assignment', id=11, parentnode=period,
                   grading_system_plugin_id=Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        period_admin = core_mommy.period_admin(period=period)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_patch_request(apikey=apikey.key, data={
            'grading_system_plugin_id': Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS
        }, queryparams='?id=11')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['grading_system_plugin_id'], Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)

    def test_patch_points_to_grade_mapper(self):
        period = mommy.make('core.Period')
        mommy.make('core.Assignment', id=11, parentnode=period,
                   points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED)
        period_admin = core_mommy.period_admin(period=period)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_patch_request(apikey=apikey.key, data={
            'points_to_grade_mapper': Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS
        }, queryparams='?id=11')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['points_to_grade_mapper'], Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS)

    def test_patch_students_can_create_groups(self):
        period = mommy.make('core.Period')
        mommy.make('core.Assignment', id=11, parentnode=period,
                   students_can_create_groups=False)
        period_admin = core_mommy.period_admin(period=period)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_patch_request(apikey=apikey.key, data={
            'students_can_create_groups': True
        }, queryparams='?id=11')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['students_can_create_groups'], True)

    def test_students_can_not_create_groups_after(self):
        period = mommy.make('core.Period')
        mommy.make('core.Assignment', id=11, parentnode=period,
                   students_can_not_create_groups_after=None)
        period_admin = core_mommy.period_admin(period=period)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_patch_request(apikey=apikey.key, data={
            'students_can_not_create_groups_after': core_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_PUBLISHING_TIME
        }, queryparams='?id=11')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['students_can_not_create_groups_after'],
                         core_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_PUBLISHING_TIME.isoformat())

    def test_patch_feedback_workflow(self):
        period = mommy.make('core.Period')
        mommy.make('core.Assignment', id=11, parentnode=period, feedback_workflow='')
        period_admin = core_mommy.period_admin(period=period)
        apikey = api_mommy.api_key_admin_permission_write(user=period_admin.user)
        response = self.mock_patch_request(apikey=apikey.key, data={
            'feedback_workflow': 'trusted-cooperative-feedback-editing'
        }, queryparams='?id=11')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['feedback_workflow'],
                         'trusted-cooperative-feedback-editing')
