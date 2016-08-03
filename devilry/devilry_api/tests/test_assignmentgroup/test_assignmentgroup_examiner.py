from model_mommy import mommy
from rest_framework.test import APITestCase

from django.conf import settings
from devilry.apps.core import devilry_core_mommy_factories
from devilry.apps.core.models import Assignment
from devilry.devilry_api import devilry_api_mommy_factories
from devilry.devilry_api.assignment_group.views.assignmentgroup_examiner import AssignmentGroupListViewExaminer
from devilry.devilry_api.tests.mixins import test_examiner_mixins, api_test_helper, test_common_mixins
from devilry.devilry_api.tests.mixins.test_common_filters_mixin import TestAssignmentFiltersExaminerMixin


class TestAssignmentGroupListView(test_common_mixins.TestReadOnlyPermissionMixin,
                                  test_examiner_mixins.TestAuthAPIKeyExaminerMixin,
                                  api_test_helper.TestCaseMixin,
                                  APITestCase):
    viewclass = AssignmentGroupListViewExaminer

    def test_unauthorized_401(self):
        response = self.mock_get_request()
        self.assertEqual(401, response.status_code)

    def test_sanity(self):
        examiner = mommy.make('core.Examiner')
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)

    def test_num_queries(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        for x in range(10):
            assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
            mommy.make('core.Examiner',
                       relatedexaminer=mommy.make('core.RelatedExaminer', active=True, user=testuser),
                       assignmentgroup__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=testuser)
        with self.assertNumQueries(4):
            self.mock_get_request(apikey=apikey.key)


class TestAssignmentGroupListViewAnonymization(api_test_helper.TestCaseMixin,
                                               APITestCase):
    viewclass = AssignmentGroupListViewExaminer

    def test_anonymization_mode_off_fullname(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = devilry_core_mommy_factories.examiner(group, fullname='Thor')
        devilry_core_mommy_factories.candidate(group, fullname='April')
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        assignment_group = response.data[0]
        self.assertEqual(assignment_group['candidates'][0]['fullname'], 'April')
        self.assertEqual(assignment_group['examiners'][0]['fullname'], 'Thor')

    def test_anonymization_mode_off_shortname(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = devilry_core_mommy_factories.examiner(group, shortname='Thor@example.com')
        devilry_core_mommy_factories.candidate(group, shortname='April@example.com')
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        assignment_group = response.data[0]
        self.assertEqual(assignment_group['candidates'][0]['shortname'], 'April@example.com')
        self.assertEqual(assignment_group['examiners'][0]['shortname'], 'Thor@example.com')

    def test_anonymization_mode_off_multiple_candidates_fullname(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        devilry_core_mommy_factories.candidate(group, fullname='April')
        devilry_core_mommy_factories.candidate(group, fullname='Alice')
        examiner = devilry_core_mommy_factories.examiner(group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        candidates = response.data[0]['candidates']
        self.assertEqual(['Alice', 'April'], [cand['fullname'] for cand in candidates])

    def test_anonymization_mode_off_multiple_candidates_shortname(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        devilry_core_mommy_factories.candidate(group, shortname='April@example.com')
        devilry_core_mommy_factories.candidate(group, shortname='Alice@example.com')
        examiner = devilry_core_mommy_factories.examiner(group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        candidates = response.data[0]['candidates']
        self.assertEqual(['Alice@example.com', 'April@example.com'], [cand['shortname'] for cand in candidates])

    def test_anonymization_mode_off_multiple_examiners_fullname(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = devilry_core_mommy_factories.examiner(group, fullname='Thor')
        devilry_core_mommy_factories.examiner(group, fullname='Balder')
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        examiners = response.data[0]['examiners']
        self.assertEqual(['Balder', 'Thor'], [exam['fullname'] for exam in examiners])

    def test_anonymization_mode_off_multiple_examiners_shortname(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = devilry_core_mommy_factories.examiner(group, shortname='Thor@example.com')
        devilry_core_mommy_factories.examiner(group, shortname='Balder@example.com')
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        examiners = response.data[0]['examiners']
        self.assertEqual(['Balder@example.com', 'Thor@example.com'], [exam['shortname'] for exam in examiners])

    def test_anonymization_mode_off_anonymous_id(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)

        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = devilry_core_mommy_factories.examiner(group)
        devilry_core_mommy_factories.candidate(group, fullname='April', shortname='April@example.com',
                                               automatic_anonymous_id='Alice')
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        candidate = response.data[0]['candidates'][0]
        self.assertEqual(candidate['fullname'], 'April')
        self.assertEqual(candidate['shortname'], 'April@example.com')

    def test_anonymization_mode_semi_fullname(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = devilry_core_mommy_factories.examiner(group, fullname='Thor')
        devilry_core_mommy_factories.candidate(group, fullname='April')
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        assignment_group = response.data[0]
        self.assertEqual(assignment_group['candidates'][0]['fullname'], 'Anonymous ID missing')
        self.assertEqual(assignment_group['examiners'][0]['fullname'], 'Thor')

    def test_anonymization_mode_semi_shortname(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = devilry_core_mommy_factories.examiner(group, shortname='Thor@example.com')
        devilry_core_mommy_factories.candidate(group, shortname='April@example.com')
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        assignment_group = response.data[0]
        self.assertEqual(assignment_group['candidates'][0]['shortname'], 'Anonymous ID missing')
        self.assertEqual(assignment_group['examiners'][0]['shortname'], 'Thor@example.com')

    def test_anonymization_mode_semi_multiple_candidates_fullname(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        devilry_core_mommy_factories.candidate(group, fullname='April')
        devilry_core_mommy_factories.candidate(group, fullname='Alice')
        examiner = devilry_core_mommy_factories.examiner(group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        candidates = response.data[0]['candidates']
        self.assertEqual(['Anonymous ID missing', 'Anonymous ID missing'], [cand['fullname'] for cand in candidates])

    def test_anonymization_mode_semi_multiple_candidates_shortname(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        devilry_core_mommy_factories.candidate(group, shortname='April@example.com')
        devilry_core_mommy_factories.candidate(group, shortname='Alice@example.com')
        examiner = devilry_core_mommy_factories.examiner(group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        candidates = response.data[0]['candidates']
        self.assertEqual(['Anonymous ID missing', 'Anonymous ID missing'], [cand['shortname'] for cand in candidates])

    def test_anonymization_mode_semi_multiple_examiners_fullname(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = devilry_core_mommy_factories.examiner(group, fullname='Thor')
        devilry_core_mommy_factories.examiner(group, fullname='Balder')
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        examiners = response.data[0]['examiners']
        self.assertEqual(['Balder', 'Thor'], [exam['fullname'] for exam in examiners])

    def test_anonymization_mode_semi_multiple_examiners_shortname(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = devilry_core_mommy_factories.examiner(group, shortname='Thor@example.com')
        devilry_core_mommy_factories.examiner(group, shortname='Balder@example.com')
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        examiners = response.data[0]['examiners']
        self.assertEqual(['Balder@example.com', 'Thor@example.com'], [exam['shortname'] for exam in examiners])

    def test_anonymization_mode_semi_anonymous_id(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)

        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = devilry_core_mommy_factories.examiner(group)
        devilry_core_mommy_factories.candidate(group, fullname='April', shortname='April@example.com',
                                               automatic_anonymous_id='Alice')
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        candidate = response.data[0]['candidates'][0]
        self.assertEqual(candidate['fullname'], 'Alice')
        self.assertEqual(candidate['shortname'], 'Alice')

    def test_anonymization_mode_full_fullname(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = devilry_core_mommy_factories.examiner(group, fullname='Thor')
        devilry_core_mommy_factories.candidate(group, fullname='April')
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        assignment_group = response.data[0]
        self.assertEqual(assignment_group['candidates'][0]['fullname'], 'Anonymous ID missing')
        self.assertEqual(assignment_group['examiners'][0]['fullname'], 'Thor')

    def test_anonymization_mode_full_shortname(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = devilry_core_mommy_factories.examiner(group, shortname='Thor@example.com')
        devilry_core_mommy_factories.candidate(group, shortname='April@example.com')
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        assignment_group = response.data[0]
        self.assertEqual(assignment_group['candidates'][0]['shortname'], 'Anonymous ID missing')
        self.assertEqual(assignment_group['examiners'][0]['shortname'], 'Thor@example.com')

    def test_anonymization_mode_full_multiple_candidates_fullname(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        devilry_core_mommy_factories.candidate(group, fullname='April')
        devilry_core_mommy_factories.candidate(group, fullname='Alice')
        examiner = devilry_core_mommy_factories.examiner(group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        candidates = response.data[0]['candidates']
        self.assertEqual(['Anonymous ID missing', 'Anonymous ID missing'], [cand['fullname'] for cand in candidates])

    def test_anonymization_mode_full_multiple_candidates_shortname(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        devilry_core_mommy_factories.candidate(group, shortname='April@example.com')
        devilry_core_mommy_factories.candidate(group, shortname='Alice@example.com')
        examiner = devilry_core_mommy_factories.examiner(group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        candidates = response.data[0]['candidates']
        self.assertEqual(['Anonymous ID missing', 'Anonymous ID missing'], [cand['shortname'] for cand in candidates])

    def test_anonymization_mode_full_multiple_examiners_fullname(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = devilry_core_mommy_factories.examiner(group, fullname='Thor')
        devilry_core_mommy_factories.examiner(group, fullname='Balder')
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        examiners = response.data[0]['examiners']
        self.assertEqual(['Balder', 'Thor'], [exam['fullname'] for exam in examiners])

    def test_anonymization_mode_full_multiple_examiners_shortname(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = devilry_core_mommy_factories.examiner(group, shortname='Thor@example.com')
        devilry_core_mommy_factories.examiner(group, shortname='Balder@example.com')
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        examiners = response.data[0]['examiners']
        self.assertEqual(['Balder@example.com', 'Thor@example.com'], [exam['shortname'] for exam in examiners])

    def test_anonymization_mode_full_anonymous_id(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)

        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        examiner = devilry_core_mommy_factories.examiner(group)
        devilry_core_mommy_factories.candidate(group, fullname='April', shortname='April@example.com',
                                               automatic_anonymous_id='Alice')
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        candidate = response.data[0]['candidates'][0]
        self.assertEqual(candidate['fullname'], 'Alice')
        self.assertEqual(candidate['shortname'], 'Alice')


class TestAssignmentGroupListViewFilters(api_test_helper.TestCaseMixin,
                                         TestAssignmentFiltersExaminerMixin,
                                         APITestCase):
    viewclass = AssignmentGroupListViewExaminer

    def test_filter_search_assignment_short_name_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       short_name='assignment1')
        examiner = mommy.make('core.Examiner',
                              relatedexaminer=mommy.make('core.RelatedExaminer', active=True),
                              assignmentgroup__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=assignment0')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_search_assignment_short_name_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       short_name='assignment1')
        examiner = mommy.make('core.Examiner',
                              relatedexaminer=mommy.make('core.RelatedExaminer', active=True),
                              assignmentgroup__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=assignment1')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.short_name, response.data[0]['assignment_short_name'])

    def test_filter_assignment_short_name_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       short_name='assignment1')
        examiner = mommy.make('core.Examiner',
                              relatedexaminer=mommy.make('core.RelatedExaminer', active=True),
                              assignmentgroup__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?assignment_short_name=assignment0')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_assignment_short_name_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       short_name='assignment1')
        examiner = mommy.make('core.Examiner',
                              relatedexaminer=mommy.make('core.RelatedExaminer', active=True),
                              assignmentgroup__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?short_name=assignment1')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.short_name, response.data[0]['assignment_short_name'])

    def test_filter_assignment_id_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', id=10)
        examiner = mommy.make('core.Examiner',
                              relatedexaminer=mommy.make('core.RelatedExaminer', active=True),
                              assignmentgroup__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?assignment_id=1')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_assignment_id_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', id=10)
        examiner = mommy.make('core.Examiner',
                              relatedexaminer=mommy.make('core.RelatedExaminer', active=True),
                              assignmentgroup__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?assignment_id=10')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.id, response.data[0]['assignment_id'])

    def test_filter_id_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment, id=10)
        examiner = devilry_core_mommy_factories.examiner(group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?id=1')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_id_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment, id=10)
        examiner = devilry_core_mommy_factories.examiner(group)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?id=10')
        self.assertEqual(200, response.status_code)
        self.assertEqual(10, response.data[0]['id'])

    def test_ordering_name_asc(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mommy.make('core.Examiner',
                   assignmentgroup=mommy.make('core.AssignmentGroup', parentnode=assignment, name='AAA'),
                   relatedexaminer=mommy.make('core.RelatedExaminer', active=True, user=testuser))
        mommy.make('core.Examiner',
                   assignmentgroup=mommy.make('core.AssignmentGroup', parentnode=assignment, name='BBB'),
                   relatedexaminer=mommy.make('core.RelatedExaminer', active=True, user=testuser))
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=testuser)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?ordering=name')
        self.assertEqual(200, response.status_code)
        self.assertListEqual(['AAA', 'BBB'], [group['name'] for group in response.data])

    def test_ordering_name_desc(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mommy.make('core.Examiner',
                   assignmentgroup=mommy.make('core.AssignmentGroup', parentnode=assignment, name='AAA'),
                   relatedexaminer=mommy.make('core.RelatedExaminer', active=True, user=testuser))
        mommy.make('core.Examiner',
                   assignmentgroup=mommy.make('core.AssignmentGroup', parentnode=assignment, name='BBB'),
                   relatedexaminer=mommy.make('core.RelatedExaminer', active=True, user=testuser))
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=testuser)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?ordering=-name')
        self.assertEqual(200, response.status_code)
        self.assertListEqual(['BBB', 'AAA'], [group['name'] for group in response.data])
