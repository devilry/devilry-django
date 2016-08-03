from model_mommy import mommy
from rest_framework.test import APITestCase

from django.conf import settings
from devilry.apps.core import devilry_core_mommy_factories
from devilry.apps.core.models import Assignment
from devilry.devilry_api import devilry_api_mommy_factories
from devilry.devilry_api.assignment_group.views.assignmentgroup_student import AssignmentGroupListViewStudent
from devilry.devilry_api.tests.mixins import test_student_mixins, api_test_helper, test_common_mixins
from devilry.devilry_api.tests.mixins.test_common_filters_mixin import TestAssignmentFiltersStudentMixin


class TestAssignmentGroupListView(test_common_mixins.TestReadOnlyPermissionMixin,
                                  test_student_mixins.TestAuthAPIKeyStudentMixin,
                                  api_test_helper.TestCaseMixin,
                                  APITestCase):
    viewclass = AssignmentGroupListViewStudent

    def test_unauthorized_401(self):
        response = self.mock_get_request()
        self.assertEqual(401, response.status_code)

    def test_sanity(self):
        candidate = mommy.make('core.Candidate')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)

    def test_id(self):
        group = mommy.make('core.AssignmentGroup', id=10)
        candidate = devilry_core_mommy_factories.candidate(group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(group.id, response.data[0]['id'])

    def test_name(self):
        group = mommy.make('core.AssignmentGroup', name='somegroup')
        candidate = devilry_core_mommy_factories.candidate(group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(group.name, response.data[0]['name'])

    def test_assignment_id(self):
        group = mommy.make('core.AssignmentGroup', parentnode__id=5)
        candidate = devilry_core_mommy_factories.candidate(group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(5, response.data[0]['assignment_id'])

    def test_assignment_short_name(self):
        group = mommy.make('core.AssignmentGroup', parentnode__short_name='assignment0')
        candidate = devilry_core_mommy_factories.candidate(group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual('assignment0', response.data[0]['assignment_short_name'])

    def test_subject_short_name(self):
        group = mommy.make('core.AssignmentGroup', parentnode__parentnode__parentnode__short_name='Duck1010')
        candidate = devilry_core_mommy_factories.candidate(group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual('Duck1010', response.data[0]['subject_short_name'])

    def test_period_short_name(self):
        group = mommy.make('core.AssignmentGroup', parentnode__parentnode__short_name='V15')
        candidate = devilry_core_mommy_factories.candidate(group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual('V15', response.data[0]['period_short_name'])

    def test_short_displayname(self):
        group = mommy.make('core.AssignmentGroup')
        candidate = devilry_core_mommy_factories.candidate(group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(group.short_displayname, response.data[0]['short_displayname'])

    def test_long_displayname(self):
        group = mommy.make('core.AssignmentGroup')
        candidate = devilry_core_mommy_factories.candidate(group)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        self.assertEqual(group.long_displayname, response.data[0]['long_displayname'])

    def test_num_queries(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        for x in range(10):
            mommy.make('core.Candidate',
                       relatedstudent__user=testuser)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=testuser)
        with self.assertNumQueries(4):
            self.mock_get_request(apikey=apikey.key)


class TestAssignmentGroupListViewAnonymization(api_test_helper.TestCaseMixin, APITestCase):
    viewclass = AssignmentGroupListViewStudent

    def test_anonymization_mode_off_fullname(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group, fullname='April')
        devilry_core_mommy_factories.examiner(group, fullname='Thor')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        assignment_group = response.data[0]
        self.assertEqual(assignment_group['candidates'][0]['fullname'], 'April')
        self.assertEqual(assignment_group['examiners'][0]['fullname'], 'Thor')

    def test_anonymization_mode_off_shortname(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group, shortname='April@example.com')
        devilry_core_mommy_factories.examiner(group, shortname='Thor@example.com')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        assignment_group = response.data[0]
        self.assertEqual(assignment_group['candidates'][0]['shortname'], 'April@example.com')
        self.assertEqual(assignment_group['examiners'][0]['shortname'], 'Thor@example.com')

    def test_anonymization_mode_off_multiple_candidates_fullname(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group, fullname='April')
        devilry_core_mommy_factories.candidate(group, fullname='Alice')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        candidates = response.data[0]['candidates']
        self.assertEqual(['Alice', 'April'], [cand['fullname'] for cand in candidates])

    def test_anonymization_mode_off_multiple_candidates_shortname(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group, shortname='April@example.com')
        devilry_core_mommy_factories.candidate(group, shortname='Alice@example.com')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        candidates = response.data[0]['candidates']
        self.assertEqual(['Alice@example.com', 'April@example.com'], [cand['shortname'] for cand in candidates])

    def test_anonymization_mode_off_multiple_examiners_fullname(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group)
        devilry_core_mommy_factories.examiner(group, fullname='Thor')
        devilry_core_mommy_factories.examiner(group, fullname='Balder')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        examiners = response.data[0]['examiners']
        self.assertEqual(['Balder', 'Thor'], [exam['fullname'] for exam in examiners])

    def test_anonymization_mode_off_multiple_examiners_shortname(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group)
        devilry_core_mommy_factories.examiner(group, shortname='Thor@example.com')
        devilry_core_mommy_factories.examiner(group, shortname='Balder@example.com')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        examiners = response.data[0]['examiners']
        self.assertEqual(['Balder@example.com', 'Thor@example.com'], [exam['shortname'] for exam in examiners])

    def test_anonymization_mode_off_anonymous_id(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group)
        devilry_core_mommy_factories.examiner(group, fullname='Balder', shortname='Balder@example.com',
                                              automatic_anonymous_id='Thor')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        examiner = response.data[0]['examiners'][0]
        self.assertEqual('Balder', examiner['fullname'])
        self.assertEqual('Balder@example.com', examiner['shortname'])

    def test_anonymization_mode_semi_fullname(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group, fullname='April')
        devilry_core_mommy_factories.examiner(group, fullname='Thor')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        assignment_group = response.data[0]
        self.assertEqual(assignment_group['candidates'][0]['fullname'], 'April')
        self.assertEqual(assignment_group['examiners'][0]['fullname'], 'Anonymous ID missing')

    def test_anonymization_mode_semi_shortname(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group, shortname='April@example.com')
        devilry_core_mommy_factories.examiner(group, shortname='Thor@example.com')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        assignment_group = response.data[0]
        self.assertEqual(assignment_group['candidates'][0]['shortname'], 'April@example.com')
        self.assertEqual(assignment_group['examiners'][0]['shortname'], 'Anonymous ID missing')

    def test_anonymization_mode_semi_multiple_candidates_fullname(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group, fullname='April')
        devilry_core_mommy_factories.candidate(group, fullname='Alice')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        candidates = response.data[0]['candidates']
        self.assertEqual(['Alice', 'April'], [cand['fullname'] for cand in candidates])

    def test_anonymization_mode_semi_multiple_candidates_shortname(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group, shortname='April@example.com')
        devilry_core_mommy_factories.candidate(group, shortname='Alice@example.com')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        candidates = response.data[0]['candidates']
        self.assertEqual(['Alice@example.com', 'April@example.com'], [cand['shortname'] for cand in candidates])

    def test_anonymization_mode_semi_multiple_examiners_fullname(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group)
        devilry_core_mommy_factories.examiner(group, fullname='Thor')
        devilry_core_mommy_factories.examiner(group, fullname='Balder')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        examiners = response.data[0]['examiners']
        self.assertEqual(['Anonymous ID missing', 'Anonymous ID missing'], [exam['fullname'] for exam in examiners])

    def test_anonymization_mode_semi_multiple_examiners_shortname(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group)
        devilry_core_mommy_factories.examiner(group, shortname='Thor@example.com')
        devilry_core_mommy_factories.examiner(group, shortname='Balder@example.com')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        examiners = response.data[0]['examiners']
        self.assertEqual(['Anonymous ID missing', 'Anonymous ID missing'], [exam['shortname'] for exam in examiners])

    def test_anonymization_mode_semi_anonymous_id(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group)
        devilry_core_mommy_factories.examiner(group,
                                              fullname='Balder',
                                              shortname='Balder@example.com',
                                              automatic_anonymous_id='Thor')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        examiner = response.data[0]['examiners'][0]
        self.assertEqual('Thor', examiner['fullname'])
        self.assertEqual('Thor', examiner['shortname'])

    def test_anonymization_mode_full_fullname(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group, fullname='April')
        devilry_core_mommy_factories.examiner(group, fullname='Thor')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        assignment_group = response.data[0]
        self.assertEqual(assignment_group['candidates'][0]['fullname'], 'April')
        self.assertEqual(assignment_group['examiners'][0]['fullname'], 'Anonymous ID missing')

    def test_anonymization_mode_full_shortname(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group, shortname='April@example.com')
        devilry_core_mommy_factories.examiner(group, shortname='Thor@example.com')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        assignment_group = response.data[0]
        self.assertEqual(assignment_group['candidates'][0]['shortname'], 'April@example.com')
        self.assertEqual(assignment_group['examiners'][0]['shortname'], 'Anonymous ID missing')

    def test_anonymization_mode_full_multiple_candidates_fullname(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group, fullname='April')
        devilry_core_mommy_factories.candidate(group, fullname='Alice')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        candidates = response.data[0]['candidates']
        self.assertEqual(['Alice', 'April'], [cand['fullname'] for cand in candidates])

    def test_anonymization_mode_full_multiple_candidates_shortname(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group, shortname='April@example.com')
        devilry_core_mommy_factories.candidate(group, shortname='Alice@example.com')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        candidates = response.data[0]['candidates']
        self.assertEqual(['Alice@example.com', 'April@example.com'], [cand['shortname'] for cand in candidates])

    def test_anonymization_mode_full_multiple_examiners_fullname(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group)
        devilry_core_mommy_factories.examiner(group, fullname='Thor')
        devilry_core_mommy_factories.examiner(group, fullname='Balder')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        examiners = response.data[0]['examiners']
        self.assertEqual(['Anonymous ID missing', 'Anonymous ID missing'], [exam['fullname'] for exam in examiners])

    def test_anonymization_mode_full_multiple_examiners_shortname(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group)
        devilry_core_mommy_factories.examiner(group, shortname='Thor@example.com')
        devilry_core_mommy_factories.examiner(group, shortname='Balder@example.com')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        examiners = response.data[0]['examiners']
        self.assertEqual(['Anonymous ID missing', 'Anonymous ID missing'], [exam['shortname'] for exam in examiners])

    def test_anonymization_mode_full_anonymous_id(self):
        assignment = mommy.make('core.Assignment', anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        candidate = devilry_core_mommy_factories.candidate(group)
        devilry_core_mommy_factories.examiner(group,
                                              fullname='Balder',
                                              shortname='Balder@example.com',
                                              automatic_anonymous_id='Thor')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key)
        self.assertEqual(200, response.status_code)
        examiner = response.data[0]['examiners'][0]
        self.assertEqual('Thor', examiner['fullname'])
        self.assertEqual('Thor', examiner['shortname'])


class TestAssignmentGroupListViewFilters(api_test_helper.TestCaseMixin,
                                         TestAssignmentFiltersStudentMixin,
                                         APITestCase):
    viewclass = AssignmentGroupListViewStudent

    def test_filter_search_assignment_short_name_not_found(self):
        assignment = mommy.make('core.Assignment', short_name='assignment1')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=assignment0')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_search_assignment_short_name_found(self):
        assignment = mommy.make('core.Assignment', short_name='assignment1')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=assignment1')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.short_name, response.data[0]['assignment_short_name'])

    def test_filter_assignment_short_name_not_found(self):
        assignment = mommy.make('core.Assignment', short_name='assignment1')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?assignment_short_name=assignment0')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_assignment_short_name_found(self):
        assignment = mommy.make('core.Assignment', short_name='assignment1')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?assignment_short_name=assignment1')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.short_name, response.data[0]['assignment_short_name'])

    def test_filter_assignment_id_not_found(self):
        assignment = mommy.make('core.Assignment', id=10)
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?assignment_id=1')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_assignment_id_found(self):
        assignment = mommy.make('core.Assignment', id=10)
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?assignment_id=10')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.id, response.data[0]['assignment_id'])

    def test_filter_id_not_found(self):
        candidate = mommy.make('core.Candidate',
                               assignment_group__id=10)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?id=1')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_id_found(self):
        candidate = mommy.make('core.Candidate',
                               assignment_group__id=10)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?id=10')
        self.assertEqual(200, response.status_code)
        self.assertEqual(10, response.data[0]['id'])

    def test_ordering_name_asc(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate', relatedstudent__user=testuser, assignment_group__name='AAA')
        mommy.make('core.Candidate', relatedstudent__user=testuser, assignment_group__name='BBB')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=testuser)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?ordering=name')
        self.assertEqual(200, response.status_code)
        self.assertListEqual(['AAA', 'BBB'], [group['name'] for group in response.data])

    def test_ordering_name_desc(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate', relatedstudent__user=testuser, assignment_group__name='AAA')
        mommy.make('core.Candidate', relatedstudent__user=testuser, assignment_group__name='BBB')
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=testuser)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?ordering=-name')
        self.assertEqual(200, response.status_code)
        self.assertListEqual(['BBB', 'AAA'], [group['name'] for group in response.data])
