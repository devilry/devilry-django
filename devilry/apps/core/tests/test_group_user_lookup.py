from django import test
from django.conf import settings

from model_bakery import baker
from devilry.apps.core import models as core_models
from devilry.apps.core.group_user_lookup import GroupUserLookup


class TestGroupUserLookupViewroleStudent(test.TestCase):
    viewrole = 'student'

    #
    # Test with user role as 'admin'.
    # This is the role of the user a student requests the name for.
    #
    def test_user_role_admin_get_unanonymized_longname(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_adminuser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Admin',
                                    shortname='testadmin@example.com')
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=test_adminuser, user_role='admin'),
                         'Test Admin (testadmin@example.com)')

    def test_user_role_admin_get_unanonymized_longname_assignment_fully_anonymized(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_adminuser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Admin',
                                    shortname='testadmin@example.com')
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=test_adminuser, user_role='admin'),
                         'Test Admin (testadmin@example.com)')

    def test_user_role_admin_get_unanonymized_longname_assignment_semi_anonymized(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_adminuser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Admin',
                                    shortname='testadmin@example.com')
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=test_adminuser, user_role='admin'),
                         'Test Admin (testadmin@example.com)')

    #
    # Test with user role as 'examiner'.
    # This is the role of the user a student requests the name for.
    #
    def test_user_role_examiner_get_unanonymized_longname(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_examineruser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Examiner', shortname='testexaminer@example.com')
        baker.make('core.RelatedExaminer', user=test_examineruser, period=testassignment.parentnode)
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=test_examineruser, user_role='examiner'),
                         'Test Examiner (testexaminer@example.com)')

    def test_user_role_examiner_get_unanonymized_shortname(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_examineruser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Examiner', shortname='testexaminer@example.com')
        baker.make('core.RelatedExaminer', user=test_examineruser, period=testassignment.parentnode)
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(
            group_user_lookup.get_plaintext_short_name_from_user(user=test_examineruser, user_role='examiner'),
            'testexaminer@example.com')

    def test_user_role_examiner_get_anonymized_longname(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_examineruser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Examiner', shortname='testexaminer@example.com')
        baker.make('core.RelatedExaminer', user=test_examineruser, period=testassignment.parentnode,
                   automatic_anonymous_id='Some anonymous name')
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=test_examineruser, user_role='examiner'),
                         'Some anonymous name')

    def test_user_role_examiner_get_anonymized_shortname(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_examineruser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Examiner',
                                       shortname='testexaminer@example.com')
        baker.make('core.RelatedExaminer', user=test_examineruser, period=testassignment.parentnode,
                   automatic_anonymous_id='Some anonymous name')
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(
            group_user_lookup.get_plaintext_short_name_from_user(user=test_examineruser, user_role='examiner'),
            'Some anonymous name')

    def test_user_role_examiner_get_anonymized_longname_relatedexaminer_does_not_exist(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_examineruser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Examiner',
                                       shortname='testexaminer@example.com')
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=test_examineruser, user_role='examiner'),
                         'User removed from semester')

    def test_user_role_examiner_user_is_examiner_and_student_is_not_anonymized_to_themselves(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Examiner',
                                      shortname='testexaminer@example.com')
        baker.make('core.RelatedExaminer', user=testuser, period=testassignment.parentnode,
                   automatic_anonymous_id='Some anonymous name')
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=testuser, user_role='examiner'),
                         'Test Examiner (testexaminer@example.com)')

    #
    # Test with user role as 'student'.
    # This is the role of the user a student requests the name for.
    #
    def test_user_role_student_get_unanonymized_longname(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_studentuser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Student',
                                      shortname='teststudent@example.com')
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=test_studentuser,
                   relatedstudent__period=testassignment.parentnode)
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=test_studentuser, user_role='student'),
                         'Test Student (teststudent@example.com)')

    def test_user_role_student_get_unanonymized_shortname(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_studentuser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Student',
                                      shortname='teststudent@example.com')
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=test_studentuser,
                   relatedstudent__period=testassignment.parentnode)
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(
            group_user_lookup.get_plaintext_short_name_from_user(user=test_studentuser, user_role='student'),
            'teststudent@example.com')

    def test_user_role_student_does_not_need_to_be_anonymized_for_other_students_assignment_fully_anonymous(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_studentuser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Student',
                                      shortname='teststudent@example.com')
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=test_studentuser,
                   relatedstudent__period=testassignment.parentnode)
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=test_studentuser, user_role='student'),
                         'Test Student (teststudent@example.com)')

    def test_user_role_student_does_not_need_to_be_anonymized_for_other_students_assignment_semi_anonymous(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_studentuser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Student',
                                      shortname='teststudent@example.com')
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=test_studentuser)
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=test_studentuser, user_role='student'),
                         'Test Student (teststudent@example.com)')


class TestGroupUserLookupViewroleExaminer(test.TestCase):
    viewrole = 'examiner'

    #
    # Test with user role as 'admin'.
    # This is the role of the user a examiner requests the name for.
    #
    def test_user_role_admin_get_unanonymized_longname(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_adminuser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Admin',
                                    shortname='testadmin@example.com')
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=test_adminuser, user_role='admin'),
                         'Test Admin (testadmin@example.com)')

    def test_user_role_admin_get_unanonymized_longname_assignment_fully_anonymized(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_adminuser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Admin',
                                    shortname='testadmin@example.com')
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=test_adminuser, user_role='admin'),
                         'Test Admin (testadmin@example.com)')

    def test_user_role_admin_get_unanonymized_longname_assignment_semi_anonymized(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_adminuser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Admin',
                                    shortname='testadmin@example.com')
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=test_adminuser, user_role='admin'),
                         'Test Admin (testadmin@example.com)')

    #
    # Test with user role as 'student'.
    # This is the role of the user an examiner requests the name for.
    #
    def test_user_role_student_get_unanonymized_longname(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_studentuser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Student', shortname='teststudent@example.com')
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=test_studentuser,
                   relatedstudent__period=testassignment.parentnode)
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=test_studentuser, user_role='student'),
                         'Test Student (teststudent@example.com)')

    def test_user_role_student_get_unanonymized_shortname(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_studentuser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Student', shortname='teststudent@example.com')
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=test_studentuser,
                   relatedstudent__period=testassignment.parentnode)
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(
            group_user_lookup.get_plaintext_short_name_from_user(user=test_studentuser, user_role='student'),
            'teststudent@example.com')

    def test_user_role_student_get_anonymized_longname_for_assignment_uses_custom_candidate_ids(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS,
                                           uses_custom_candidate_ids=True)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_studentuser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Student', shortname='teststudent@example.com')
        baker.make('core.Candidate', assignment_group=testgroup,
                   relatedstudent__user=test_studentuser, candidate_id='1234',
                   relatedstudent__period=testassignment.parentnode)
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=test_studentuser, user_role='student'),
                         '1234')

    def test_user_role_student_get_anonymized_longname(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_studentuser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Student', shortname='teststudent@example.com')
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=test_studentuser,
                   relatedstudent__automatic_anonymous_id='Some anonymous name',
                   relatedstudent__period=testassignment.parentnode)
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=test_studentuser, user_role='student'),
                         'Some anonymous name')

    def test_user_role_student_get_anonymized_shortname(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_studentuser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Student', shortname='teststudent@example.com')
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=test_studentuser,
                   relatedstudent__automatic_anonymous_id='Some anonymous name',
                   relatedstudent__period=testassignment.parentnode)
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(
            group_user_lookup.get_plaintext_short_name_from_user(user=test_studentuser, user_role='student'),
            'Some anonymous name')

    def test_user_role_student_get_anonymized_longname_candidate_does_not_exist(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_studentuser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Student', shortname='teststudent@example.com')
        baker.make('core.RelatedStudent', period=testassignment.parentnode, user=test_studentuser,
                   automatic_anonymous_id='Some anonymous name')
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=test_studentuser, user_role='student'),
                         'Some anonymous name')

    def test_user_role_student_get_anonymized_longname_no_candidate_or_relatedstudent(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_studentuser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Student', shortname='teststudent@example.com')
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=test_studentuser, user_role='student'),
                         'User removed from semester')

    def test_user_role_student_user_is_student_and_examiner_is_not_anonymized_to_themselves(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Student',
                                      shortname='teststudent@example.com')
        baker.make('core.Candidate', assignment_group=testgroup, relatedstudent__user=testuser,
                   relatedstudent__automatic_anonymous_id='Some anonymous name',
                   relatedstudent__period=testassignment.parentnode)
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=testuser, user_role='student'),
                         'Test Student (teststudent@example.com)')

    #
    # Test with user role as 'examiner'.
    # This is the role of the user an examiner requests the name for.
    #
    def test_user_role_examiner_get_unanonymized_longname(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_examineruser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Examiner', shortname='testexaminer@example.com')
        baker.make('core.RelatedExaminer', user=test_examineruser, period=testassignment.parentnode)
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=test_examineruser, user_role='examiner'),
                         'Test Examiner (testexaminer@example.com)')

    def test_user_role_examiner_get_unanonymized_shortname(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_examineruser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Examiner', shortname='testexaminer@example.com')
        baker.make('core.RelatedExaminer', user=test_examineruser, period=testassignment.parentnode)
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(
            group_user_lookup.get_plaintext_short_name_from_user(user=test_examineruser, user_role='examiner'),
            'testexaminer@example.com')

    def test_user_role_examiner_does_not_need_to_be_anonymized_assignment_fully_anonymous(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_examineruser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Examiner', shortname='testexaminer@example.com')
        baker.make('core.RelatedExaminer', user=test_examineruser, period=testassignment.parentnode,
                   automatic_anonymous_id='Some anonymous name')
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=test_examineruser, user_role='examiner'),
                         'Test Examiner (testexaminer@example.com)')

    def test_user_role_examiner_does_not_need_to_be_anonymized_assignment_semi_anonymous(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_examineruser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Examiner', shortname='testexaminer@example.com')
        baker.make('core.RelatedExaminer', user=test_examineruser, period=testassignment.parentnode,
                   automatic_anonymous_id='Some anonymous name')
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=test_examineruser, user_role='examiner'),
                         'Test Examiner (testexaminer@example.com)')


class TestGroupUserLookupViewroleAdmin(test.TestCase):
    viewrole = 'admin'

    def test_user_role_admin_get_unanonymized_longname(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_adminuser = baker.make(settings.AUTH_USER_MODEL, fullname='Test Admin',
                                    shortname='testadmin@example.com')
        group_user_lookup = GroupUserLookup(assignment=testassignment, group=testgroup,
                                            requestuser=testuser, requestuser_devilryrole=self.viewrole)
        self.assertEqual(group_user_lookup.get_long_name_from_user(user=test_adminuser, user_role='admin'),
                         'Test Admin (testadmin@example.com)')


