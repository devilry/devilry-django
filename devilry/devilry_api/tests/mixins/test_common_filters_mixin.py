from model_mommy import mommy
from devilry.devilry_api import devilry_api_mommy_factories
from devilry.apps.core import devilry_core_mommy_factories as core_mommy


class TestAssignmentFiltersStudentMixin(object):
    def test_filter_search_subject_short_name_not_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__parentnode__short_name='duckduck1010',
                                parentnode__short_name='456',
                                short_name='456')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=123')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_search_subject_short_name_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__parentnode__short_name='duckduck1010')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=duckduck1010')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.parentnode.parentnode.short_name, response.data[0]['subject_short_name'])

    def test_filter_search_period_short_name_not_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__short_name='asd',
                                parentnode__parentnode__short_name='456',
                                short_name='456')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=S16')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_search_period_short_name_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__short_name='S15')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=S15')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.parentnode.short_name, response.data[0]['period_short_name'])

    def test_filter_subject_short_name_not_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__parentnode__short_name='duck1010')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?subject_short_name=duck1000')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_subject_short_name_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__parentnode__short_name='duck1010')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?subject_short_name=duck1010')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.parentnode.parentnode.short_name, response.data[0]['subject_short_name'])

    def test_filter_period_short_name_not_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__short_name='S07')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?period_short_name=S15')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_period_short_name_found(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__short_name='S15')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_student_permission_read(user=candidate.relatedstudent.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?period_short_name=S15')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.parentnode.short_name, response.data[0]['period_short_name'])


class TestAssignmentFiltersExaminerMixin(object):

    def test_filter_search_subject_short_name_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       parentnode__parentnode__short_name='duckduck1010',
                                       parentnode__short_name='456',
                                       short_name='456'
                                       )
        examiner = mommy.make('core.Examiner',
                              relatedexaminer=mommy.make('core.RelatedExaminer', active=True),
                              assignmentgroup__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=123')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_search_subject_short_name_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       parentnode__parentnode__short_name='duckduck1010')
        examiner = mommy.make('core.Examiner',
                              relatedexaminer=mommy.make('core.RelatedExaminer', active=True),
                              assignmentgroup__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=duckduck1010')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.parentnode.parentnode.short_name, response.data[0]['subject_short_name'])

    def test_filter_search_period_short_name_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       parentnode__short_name='asd',
                                       parentnode__parentnode__short_name='456',
                                       short_name='456'
                                       )
        examiner = mommy.make('core.Examiner',
                              relatedexaminer=mommy.make('core.RelatedExaminer', active=True),
                              assignmentgroup__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=S16')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_search_period_short_name_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       parentnode__short_name='S15')
        examiner = mommy.make('core.Examiner',
                              relatedexaminer=mommy.make('core.RelatedExaminer', active=True),
                              assignmentgroup__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=S15')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.parentnode.short_name, response.data[0]['period_short_name'])

    def test_filter_subject_short_name_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       parentnode__parentnode__short_name='duck1010')
        examiner = mommy.make('core.Examiner',
                              relatedexaminer=mommy.make('core.RelatedExaminer', active=True),
                              assignmentgroup__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?subject_short_name=duck1000')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_subject_short_name_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       parentnode__parentnode__short_name='duck1010')
        examiner = mommy.make('core.Examiner',
                              relatedexaminer=mommy.make('core.RelatedExaminer', active=True),
                              assignmentgroup__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?subject_short_name=duck1010')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.parentnode.parentnode.short_name, response.data[0]['subject_short_name'])

    def test_filter_period_short_name_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       parentnode__short_name='S07')
        examiner = mommy.make('core.Examiner',
                              relatedexaminer=mommy.make('core.RelatedExaminer', active=True),
                              assignmentgroup__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?period_short_name=S15')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_period_short_name_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       parentnode__short_name='S15')
        examiner = mommy.make('core.Examiner',
                              relatedexaminer=mommy.make('core.RelatedExaminer', active=True),
                              assignmentgroup__parentnode=assignment)
        apikey = devilry_api_mommy_factories.api_key_examiner_permission_read(user=examiner.relatedexaminer.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?period_short_name=S15')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.parentnode.short_name, response.data[0]['period_short_name'])


class TestAssignmentFiltersPeriodAdminMixin(object):

    def test_filter_search_subject_short_name_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       parentnode__parentnode__short_name='duckduck1010',
                                       parentnode__short_name='spriiiing',
                                       short_name='assignment1')
        mommy.make('core.AssignmentGroup', parentnode=assignment)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = devilry_api_mommy_factories.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=123')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_search_subject_short_name_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       parentnode__parentnode__short_name='duckduck1010')
        mommy.make('core.AssignmentGroup', parentnode=assignment)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = devilry_api_mommy_factories.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=duckduck1010')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.parentnode.parentnode.short_name, response.data[0]['subject_short_name'])

    def test_filter_search_period_short_name_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       parentnode__short_name='asd',
                                       parentnode__parentnode__short_name='456',
                                       short_name='456'
                                       )
        mommy.make('core.AssignmentGroup', parentnode=assignment)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = devilry_api_mommy_factories.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=S16')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_search_period_short_name_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       parentnode__short_name='S15')
        mommy.make('core.AssignmentGroup', parentnode=assignment)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = devilry_api_mommy_factories.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?search=S15')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.parentnode.short_name, response.data[0]['period_short_name'])

    def test_filter_subject_short_name_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       parentnode__parentnode__short_name='duck1010')
        mommy.make('core.AssignmentGroup', parentnode=assignment)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = devilry_api_mommy_factories.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?subject_short_name=duck1000')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_subject_short_name_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       parentnode__parentnode__short_name='duck1010')
        mommy.make('core.AssignmentGroup', parentnode=assignment)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = devilry_api_mommy_factories.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?subject_short_name=duck1010')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.parentnode.parentnode.short_name, response.data[0]['subject_short_name'])

    def test_filter_period_short_name_not_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       parentnode__short_name='S07')
        mommy.make('core.AssignmentGroup', parentnode=assignment)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = devilry_api_mommy_factories.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?period_short_name=S15')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_filter_period_short_name_found(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       parentnode__short_name='S15')
        mommy.make('core.AssignmentGroup', parentnode=assignment)
        period_admin = core_mommy.period_admin(period=assignment.parentnode)
        apikey = devilry_api_mommy_factories.api_key_admin_permission_read(user=period_admin.user)
        response = self.mock_get_request(apikey=apikey.key,
                                         queryparams='?period_short_name=S15')
        self.assertEqual(200, response.status_code)
        self.assertEqual(assignment.parentnode.short_name, response.data[0]['period_short_name'])
