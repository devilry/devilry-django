import htmls
import mock
from django import test
from django.template.loader import render_to_string
from model_mommy import mommy

from devilry.apps.core.models import Assignment
from devilry.apps.core.templatetags import devilry_core_tags


class TestDevilrySingleCandidateLongDisplayname(test.TestCase):
    def test_nonanonymous_cssclass(self):
        assignment = mommy.make('core.Assignment')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-candidate-long-displayname.django.html',
                devilry_core_tags.devilry_single_candidate_long_displayname(assignment, candidate, 'student')))
        self.assertTrue(selector.exists('.devilry-user-verbose-inline'))
        self.assertFalse(selector.exists('.devilry-core-candidate-anonymous-name'))

    def test_nonanonymous_without_fullname(self):
        assignment = mommy.make('core.Assignment')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-candidate-long-displayname.django.html',
                devilry_core_tags.devilry_single_candidate_long_displayname(assignment, candidate, 'student')))
        self.assertEqual('testuser',
                         selector.one('.devilry-user-verbose-inline').alltext_normalized)

    def test_nonanonymous_with_fullname(self):
        assignment = mommy.make('core.Assignment')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser',
                               relatedstudent__user__fullname='Test User')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-candidate-long-displayname.django.html',
                devilry_core_tags.devilry_single_candidate_long_displayname(assignment, candidate, 'student')))
        self.assertEqual('Test User(testuser)',
                         selector.one('.devilry-user-verbose-inline').alltext_normalized)

    def test_anonymous_cssclass(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-candidate-long-displayname.django.html',
                devilry_core_tags.devilry_single_candidate_long_displayname(assignment, candidate, 'examiner')))
        self.assertFalse(selector.exists('.devilry-user-verbose-inline'))
        self.assertTrue(selector.exists('.devilry-core-candidate-anonymous-name'))

    def test_anonymous(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__automatic_anonymous_id='MyAnonymousId',
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-candidate-long-displayname.django.html',
                devilry_core_tags.devilry_single_candidate_long_displayname(assignment, candidate, 'examiner')))
        self.assertEqual('MyAnonymousId',
                         selector.one('.devilry-core-candidate-anonymous-name').alltext_normalized)


class TestDevilrySingleCandidateShortDisplayname(test.TestCase):
    def test_nonanonymous_cssclass(self):
        assignment = mommy.make('core.Assignment')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-candidate-short-displayname.django.html',
                devilry_core_tags.devilry_single_candidate_short_displayname(assignment, candidate, 'student')))
        self.assertTrue(selector.exists('.devilry-core-candidate-shortname'))
        self.assertFalse(selector.exists('.devilry-core-candidate-anonymous-name'))

    def test_nonanonymous_without_fullname(self):
        assignment = mommy.make('core.Assignment')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-candidate-short-displayname.django.html',
                devilry_core_tags.devilry_single_candidate_short_displayname(assignment, candidate, 'student')))
        self.assertEqual('testuser',
                         selector.one('.devilry-core-candidate-shortname').alltext_normalized)

    def test_nonanonymous_with_fullname(self):
        assignment = mommy.make('core.Assignment')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser',
                               relatedstudent__user__fullname='Test User')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-candidate-short-displayname.django.html',
                devilry_core_tags.devilry_single_candidate_short_displayname(assignment, candidate, 'student')))
        self.assertEqual('testuser',
                         selector.one('.devilry-core-candidate-shortname').alltext_normalized)

    def test_anonymous_cssclass(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-candidate-short-displayname.django.html',
                devilry_core_tags.devilry_single_candidate_short_displayname(assignment, candidate, 'examiner')))
        self.assertFalse(selector.exists('.devilry-core-candidate-shortname'))
        self.assertTrue(selector.exists('.devilry-core-candidate-anonymous-name'))

    def test_anonymous(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__automatic_anonymous_id='MyAnonymousId',
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-candidate-short-displayname.django.html',
                devilry_core_tags.devilry_single_candidate_short_displayname(assignment, candidate, 'examiner')))
        self.assertEqual('MyAnonymousId',
                         selector.one('.devilry-core-candidate-anonymous-name').alltext_normalized)


class TestDevilrySingleExaminerLongDisplayname(test.TestCase):
    def test_nonanonymous_cssclass(self):
        assignment = mommy.make('core.Assignment')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-examiner-long-displayname.django.html',
                devilry_core_tags.devilry_single_examiner_long_displayname(assignment, examiner, 'examiner')))
        self.assertTrue(selector.exists('.devilry-user-verbose-inline'))
        self.assertFalse(selector.exists('.devilry-core-examiner-anonymous-name'))

    def test_nonanonymous_without_fullname(self):
        assignment = mommy.make('core.Assignment')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-examiner-long-displayname.django.html',
                devilry_core_tags.devilry_single_examiner_long_displayname(assignment, examiner, 'examiner')))
        self.assertEqual('testuser',
                         selector.one('.devilry-user-verbose-inline').alltext_normalized)

    def test_nonanonymous_with_fullname(self):
        assignment = mommy.make('core.Assignment')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser',
                              relatedexaminer__user__fullname='Test User')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-examiner-long-displayname.django.html',
                devilry_core_tags.devilry_single_examiner_long_displayname(assignment, examiner, 'examiner')))
        self.assertEqual('Test User(testuser)',
                         selector.one('.devilry-user-verbose-inline').alltext_normalized)

    def test_anonymous_cssclass(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-examiner-long-displayname.django.html',
                devilry_core_tags.devilry_single_examiner_long_displayname(assignment, examiner, 'student')))
        self.assertFalse(selector.exists('.devilry-user-verbose-inline'))
        self.assertTrue(selector.exists('.devilry-core-examiner-anonymous-name'))

    def test_anonymous(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__automatic_anonymous_id='MyAnonymousId',
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-examiner-long-displayname.django.html',
                devilry_core_tags.devilry_single_examiner_long_displayname(assignment, examiner, 'student')))
        self.assertEqual('MyAnonymousId',
                         selector.one('.devilry-core-examiner-anonymous-name').alltext_normalized)


class TestDevilrySingleExaminerShortDisplayname(test.TestCase):
    def test_nonanonymous_cssclass(self):
        assignment = mommy.make('core.Assignment')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-examiner-short-displayname.django.html',
                devilry_core_tags.devilry_single_examiner_short_displayname(assignment, examiner, 'examiner')))
        self.assertTrue(selector.exists('.devilry-core-examiner-shortname'))
        self.assertFalse(selector.exists('.devilry-core-examiner-anonymous-name'))

    def test_nonanonymous_without_fullname(self):
        assignment = mommy.make('core.Assignment')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-examiner-short-displayname.django.html',
                devilry_core_tags.devilry_single_examiner_short_displayname(assignment, examiner, 'examiner')))
        self.assertEqual('testuser',
                         selector.one('.devilry-core-examiner-shortname').alltext_normalized)

    def test_nonanonymous_with_fullname(self):
        assignment = mommy.make('core.Assignment')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser',
                              relatedexaminer__user__fullname='Test User')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-examiner-short-displayname.django.html',
                devilry_core_tags.devilry_single_examiner_short_displayname(assignment, examiner, 'examiner')))
        self.assertEqual('testuser',
                         selector.one('.devilry-core-examiner-shortname').alltext_normalized)

    def test_anonymous_cssclass(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-examiner-short-displayname.django.html',
                devilry_core_tags.devilry_single_examiner_short_displayname(assignment, examiner, 'student')))
        self.assertFalse(selector.exists('.devilry-core-examiner-shortname'))
        self.assertTrue(selector.exists('.devilry-core-examiner-anonymous-name'))

    def test_anonymous(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__automatic_anonymous_id='MyAnonymousId',
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-examiner-short-displayname.django.html',
                devilry_core_tags.devilry_single_examiner_short_displayname(assignment, examiner, 'student')))
        self.assertEqual('MyAnonymousId',
                         selector.one('.devilry-core-examiner-anonymous-name').alltext_normalized)


class TestDevilryMultipleCandidatesLongDisplayname(test.TestCase):
    def test_nonanonymous_cssclass(self):
        assignment = mommy.make('core.Assignment')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_long_displayname(assignment, [candidate], 'student')))
        self.assertTrue(selector.exists('.devilry-user-verbose-inline'))
        self.assertFalse(selector.exists('.devilry-core-candidate-anonymous-name'))

    def test_empty(self):
        assignment = mommy.make('core.Assignment')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_long_displayname(assignment, [], 'student')))
        self.assertEqual(
            'no students in group',
            selector.one('.devilry-core-no-candidates-in-group').alltext_normalized)
        self.assertFalse(selector.exists('.devilry-user-verbose-inline'))
        self.assertFalse(selector.exists('.devilry-core-candidate-anonymous-name'))

    def test_nonanonymous_without_fullname(self):
        assignment = mommy.make('core.Assignment')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_long_displayname(assignment, [candidate], 'student')))
        self.assertEqual('testuser',
                         selector.one('.devilry-user-verbose-inline').alltext_normalized)

    def test_nonanonymous_with_fullname(self):
        assignment = mommy.make('core.Assignment')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser',
                               relatedstudent__user__fullname='Test User')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_long_displayname(assignment, [candidate], 'student')))
        self.assertEqual('Test User(testuser)',
                         selector.one('.devilry-user-verbose-inline').alltext_normalized)

    def test_nonanonymous_multiple_candidates(self):
        assignment = mommy.make('core.Assignment')
        candidate1 = mommy.make('core.Candidate',
                                assignment_group__parentnode=assignment,
                                relatedstudent__user__shortname='testuser1')
        candidate2 = mommy.make('core.Candidate',
                                assignment_group__parentnode=assignment,
                                relatedstudent__user__shortname='testuser2',
                                relatedstudent__user__fullname='Test User 2')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_long_displayname(
                    assignment, [candidate1, candidate2], 'student')))
        names = [element.alltext_normalized
                 for element in selector.list('.devilry-user-verbose-inline')]
        self.assertEqual(['testuser1', 'Test User 2(testuser2)'], names)

    def test_anonymous_cssclass(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_long_displayname(assignment, [candidate], 'examiner')))
        self.assertFalse(selector.exists('.devilry-user-verbose-inline'))
        self.assertTrue(selector.exists('.devilry-core-candidate-anonymous-name'))

    def test_anonymous(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__automatic_anonymous_id='MyAnonymousId',
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_long_displayname(assignment, [candidate], 'examiner')))
        self.assertEqual('MyAnonymousId',
                         selector.one('.devilry-core-candidate-anonymous-name').alltext_normalized)

    def test_anonymous_multiple_candidates(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        candidate1 = mommy.make('core.Candidate',
                                assignment_group__parentnode=assignment,
                                relatedstudent__automatic_anonymous_id='MyAnonymousId1',
                                relatedstudent__user__shortname='testuser1')
        candidate2 = mommy.make('core.Candidate',
                                assignment_group__parentnode=assignment,
                                relatedstudent__automatic_anonymous_id='MyAnonymousId2',
                                relatedstudent__user__shortname='testuser2')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_long_displayname(
                    assignment, [candidate1, candidate2], 'examiner')))
        names = [element.alltext_normalized
                 for element in selector.list('.devilry-core-candidate-anonymous-name')]
        self.assertEqual(['MyAnonymousId1', 'MyAnonymousId2'], names)


class TestDevilryMultipleCandidatesShortDisplayname(test.TestCase):
    def test_nonanonymous_cssclass(self):
        assignment = mommy.make('core.Assignment')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_short_displayname(assignment, [candidate], 'student')))
        self.assertTrue(selector.exists('.devilry-core-candidate-shortname'))
        self.assertFalse(selector.exists('.devilry-core-candidate-anonymous-name'))

    def test_empty(self):
        assignment = mommy.make('core.Assignment')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_short_displayname(assignment, [], 'student')))
        self.assertEqual(
            'no students in group',
            selector.one('.devilry-core-no-candidates-in-group').alltext_normalized)
        self.assertFalse(selector.exists('.devilry-user-verbose-inline'))
        self.assertFalse(selector.exists('.devilry-core-candidate-anonymous-name'))

    def test_nonanonymous_without_fullname(self):
        assignment = mommy.make('core.Assignment')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_short_displayname(assignment, [candidate], 'student')))
        self.assertEqual('testuser',
                         selector.one('.devilry-core-candidate-shortname').alltext_normalized)

    def test_nonanonymous_with_fullname(self):
        assignment = mommy.make('core.Assignment')
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser',
                               relatedstudent__user__fullname='Test User')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_short_displayname(assignment, [candidate], 'student')))
        self.assertEqual('testuser',
                         selector.one('.devilry-core-candidate-shortname').alltext_normalized)

    def test_nonanonymous_multiple_candidates(self):
        assignment = mommy.make('core.Assignment')
        candidate1 = mommy.make('core.Candidate',
                                assignment_group__parentnode=assignment,
                                relatedstudent__user__shortname='testuser1')
        candidate2 = mommy.make('core.Candidate',
                                assignment_group__parentnode=assignment,
                                relatedstudent__user__shortname='testuser2',
                                relatedstudent__user__fullname='Test User 2')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_short_displayname(
                    assignment, [candidate1, candidate2], 'student')))
        names = [element.alltext_normalized
                 for element in selector.list('.devilry-core-candidate-shortname')]
        self.assertEqual(['testuser1', 'testuser2'], names)

    def test_anonymous_cssclass(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_short_displayname(assignment, [candidate], 'examiner')))
        self.assertFalse(selector.exists('.devilry-core-candidate-shortname'))
        self.assertTrue(selector.exists('.devilry-core-candidate-anonymous-name'))

    def test_anonymous(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate = mommy.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__automatic_anonymous_id='MyAnonymousId',
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_short_displayname(assignment, [candidate], 'examiner')))
        self.assertEqual('MyAnonymousId',
                         selector.one('.devilry-core-candidate-anonymous-name').alltext_normalized)

    def test_anonymous_multiple_candidates(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        candidate1 = mommy.make('core.Candidate',
                                assignment_group__parentnode=assignment,
                                relatedstudent__automatic_anonymous_id='MyAnonymousId1',
                                relatedstudent__user__shortname='testuser1')
        candidate2 = mommy.make('core.Candidate',
                                assignment_group__parentnode=assignment,
                                relatedstudent__automatic_anonymous_id='MyAnonymousId2',
                                relatedstudent__user__shortname='testuser2')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_short_displayname(
                    assignment, [candidate1, candidate2], 'examiner')))
        names = [element.alltext_normalized
                 for element in selector.list('.devilry-core-candidate-anonymous-name')]
        self.assertEqual(['MyAnonymousId1', 'MyAnonymousId2'], names)


class TestDevilryMultipleExaminersLongDisplayname(test.TestCase):
    def test_nonanonymous_cssclass(self):
        assignment = mommy.make('core.Assignment')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_long_displayname(assignment, [examiner], 'examiner')))
        self.assertTrue(selector.exists('.devilry-user-verbose-inline'))
        self.assertFalse(selector.exists('.devilry-core-examiner-anonymous-name'))

    def test_empty(self):
        assignment = mommy.make('core.Assignment')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_long_displayname(assignment, [], 'examiner')))
        self.assertEqual(
            'no examiner(s)',
            selector.one('.devilry-core-no-examiners-for-group').alltext_normalized)
        self.assertFalse(selector.exists('.devilry-user-verbose-inline'))
        self.assertFalse(selector.exists('.devilry-core-examiner-anonymous-name'))

    def test_nonanonymous_without_fullname(self):
        assignment = mommy.make('core.Assignment')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_long_displayname(assignment, [examiner], 'examiner')))
        self.assertEqual('testuser',
                         selector.one('.devilry-user-verbose-inline').alltext_normalized)

    def test_nonanonymous_multiple_examiners(self):
        assignment = mommy.make('core.Assignment')
        examiner1 = mommy.make('core.Examiner',
                               assignment_group__parentnode=assignment,
                               relatedexaminer__user__shortname='testuser1')
        examiner2 = mommy.make('core.Examiner',
                               assignment_group__parentnode=assignment,
                               relatedexaminer__user__fullname='Test User 2',
                               relatedexaminer__user__shortname='testuser2')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_long_displayname(
                    assignment, [examiner1, examiner2], 'examiner')))
        names = [element.alltext_normalized
                 for element in selector.list('.devilry-user-verbose-inline')]
        self.assertEqual(['testuser1', 'Test User 2(testuser2)'], names)

    def test_nonanonymous_with_fullname(self):
        assignment = mommy.make('core.Assignment')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser',
                              relatedexaminer__user__fullname='Test User')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_long_displayname(assignment, [examiner], 'examiner')))
        self.assertEqual('Test User(testuser)',
                         selector.one('.devilry-user-verbose-inline').alltext_normalized)

    def test_anonymous_cssclass(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_long_displayname(assignment, [examiner], 'student')))
        self.assertFalse(selector.exists('.devilry-user-verbose-inline'))
        self.assertTrue(selector.exists('.devilry-core-examiner-anonymous-name'))

    def test_anonymous(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__automatic_anonymous_id='MyAnonymousId',
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_long_displayname(assignment, [examiner], 'student')))
        self.assertEqual('MyAnonymousId',
                         selector.one('.devilry-core-examiner-anonymous-name').alltext_normalized)

    def test_anonymous_multiple_examiners(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        examiner1 = mommy.make('core.Examiner',
                               assignment_group__parentnode=assignment,
                               relatedexaminer__automatic_anonymous_id='MyAnonymousId1',
                               relatedexaminer__user__shortname='testuser1')
        examiner2 = mommy.make('core.Examiner',
                               assignment_group__parentnode=assignment,
                               relatedexaminer__automatic_anonymous_id='MyAnonymousId2',
                               relatedexaminer__user__shortname='testuser2')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_long_displayname(
                    assignment, [examiner1, examiner2], 'student')))
        names = [element.alltext_normalized
                 for element in selector.list('.devilry-core-examiner-anonymous-name')]
        self.assertEqual(['MyAnonymousId1', 'MyAnonymousId2'], names)


class TestDevilryMultipleExaminersShortDisplayname(test.TestCase):
    def test_nonanonymous_cssclass(self):
        assignment = mommy.make('core.Assignment')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_short_displayname(assignment, [examiner], 'examiner')))
        self.assertTrue(selector.exists('.devilry-core-examiner-shortname'))
        self.assertFalse(selector.exists('.devilry-core-examiner-anonymous-name'))

    def test_empty(self):
        assignment = mommy.make('core.Assignment')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_short_displayname(assignment, [], 'examiner')))
        self.assertEqual(
            'no examiner(s)',
            selector.one('.devilry-core-no-examiners-for-group').alltext_normalized)
        self.assertFalse(selector.exists('.devilry-user-verbose-inline'))
        self.assertFalse(selector.exists('.devilry-core-examiner-anonymous-name'))

    def test_nonanonymous_without_fullname(self):
        assignment = mommy.make('core.Assignment')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_short_displayname(assignment, [examiner], 'examiner')))
        self.assertEqual('testuser',
                         selector.one('.devilry-core-examiner-shortname').alltext_normalized)

    def test_nonanonymous_with_fullname(self):
        assignment = mommy.make('core.Assignment')
        examiner = mommy.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser',
                              relatedexaminer__user__fullname='Test User')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_short_displayname(assignment, [examiner], 'examiner')))
        self.assertEqual('testuser',
                         selector.one('.devilry-core-examiner-shortname').alltext_normalized)

    def test_nonanonymous_multiple_examiners(self):
        assignment = mommy.make('core.Assignment')
        examiner1 = mommy.make('core.Examiner',
                               assignment_group__parentnode=assignment,
                               relatedexaminer__user__shortname='testuser1')
        examiner2 = mommy.make('core.Examiner',
                               assignment_group__parentnode=assignment,
                               relatedexaminer__user__fullname='Test User 2',
                               relatedexaminer__user__shortname='testuser2')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_short_displayname(
                    assignment, [examiner1, examiner2], 'examiner')))
        names = [element.alltext_normalized
                 for element in selector.list('.devilry-core-examiner-shortname')]
        self.assertEqual(['testuser1', 'testuser2'], names)

    def test_anonymous_cssclass(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_short_displayname(assignment, [examiner], 'student')))
        self.assertFalse(selector.exists('.devilry-core-examiner-shortname'))
        self.assertTrue(selector.exists('.devilry-core-examiner-anonymous-name'))

    def test_anonymous(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        examiner = mommy.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__automatic_anonymous_id='MyAnonymousId',
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_short_displayname(assignment, [examiner], 'student')))
        self.assertEqual('MyAnonymousId',
                         selector.one('.devilry-core-examiner-anonymous-name').alltext_normalized)

    def test_anonymous_multiple_examiners(self):
        assignment = mommy.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        examiner1 = mommy.make('core.Examiner',
                               assignment_group__parentnode=assignment,
                               relatedexaminer__automatic_anonymous_id='MyAnonymousId1',
                               relatedexaminer__user__shortname='testuser1')
        examiner2 = mommy.make('core.Examiner',
                               assignment_group__parentnode=assignment,
                               relatedexaminer__automatic_anonymous_id='MyAnonymousId2',
                               relatedexaminer__user__shortname='testuser2')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_short_displayname(
                    assignment, [examiner1, examiner2], 'student')))
        names = [element.alltext_normalized
                 for element in selector.list('.devilry-core-examiner-anonymous-name')]
        self.assertEqual(['MyAnonymousId1', 'MyAnonymousId2'], names)


class MockGroupStatusGroup(object):
    def __init__(self, is_corrected=False, is_waiting_for_feedback=False,
                 is_waiting_for_deliveries=False):
        self.is_corrected = is_corrected
        self.is_waiting_for_feedback = is_waiting_for_feedback
        self.is_waiting_for_deliveries = is_waiting_for_deliveries


class TestDevilryGroupstatus(test.TestCase):
    def test_is_corrected(self):
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/groupstatus.django.html',
                devilry_core_tags.devilry_groupstatus(MockGroupStatusGroup(is_corrected=True))))
        self.assertTrue(selector.exists('.devilry-core-groupstatus'))
        self.assertFalse(selector.exists('.devilry-core-groupstatus-waiting-for-feedback'))
        self.assertFalse(selector.exists('.devilry-core-groupstatus-deliveries'))
        self.assertEqual(
            'corrected',
            selector.one('.devilry-core-groupstatus-corrected').alltext_normalized)

    def test_is_waiting_for_feedback(self):
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/groupstatus.django.html',
                devilry_core_tags.devilry_groupstatus(MockGroupStatusGroup(is_waiting_for_feedback=True))))
        self.assertTrue(selector.exists('.devilry-core-groupstatus'))
        self.assertFalse(selector.exists('.devilry-core-groupstatus-corrected'))
        self.assertFalse(selector.exists('.devilry-core-groupstatus-deliveries'))
        self.assertTrue(
            'waiting for feedback',
            selector.one('.devilry-core-groupstatus-waiting-for-feedback').alltext_normalized)

    def test_is_waiting_for_deliveries(self):
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/groupstatus.django.html',
                devilry_core_tags.devilry_groupstatus(MockGroupStatusGroup(is_waiting_for_deliveries=True))))
        self.assertTrue(selector.exists('.devilry-core-groupstatus'))
        self.assertFalse(selector.exists('.devilry-core-groupstatus-corrected'))
        self.assertFalse(selector.exists('.devilry-core-groupstatus-waiting-for-feedback'))
        self.assertTrue(
            'waiting for deliveries',
            selector.one('.devilry-core-groupstatus-waiting-for-deliveries').alltext_normalized)


class TestDevilryGrade(test.TestCase):
    def test_grade_passed_failed_failed(self):
        testassignment = mommy.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade.django.html',
                devilry_core_tags.devilry_grade(testassignment, 0)))
        self.assertTrue(selector.exists('.devilry-core-grade.devilry-core-grade-passed-failed'))
        self.assertEqual(
            'failed',
            selector.one('.devilry-core-grade').alltext_normalized)

    def test_grade_passed_failed_passed(self):
        testassignment = mommy.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade.django.html',
                devilry_core_tags.devilry_grade(testassignment, 10)))
        self.assertTrue(selector.exists('.devilry-core-grade.devilry-core-grade-passed-failed'))
        self.assertEqual(
            'passed',
            selector.one('.devilry-core-grade').alltext_normalized)

    def test_grade_passedorfailed_raw_points(self):
        testassignment = mommy.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS,
            max_points=100)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade.django.html',
                devilry_core_tags.devilry_grade(testassignment, 10)))
        self.assertTrue(selector.exists('.devilry-core-grade.devilry-core-grade-raw-points'))
        self.assertEqual(
            '10/100',
            selector.one('.devilry-core-grade').alltext_normalized)

    def test_grade_passedorfailed_custom_table(self):
        testassignment = mommy.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE)
        point_to_grade_map = mommy.make('core.PointToGradeMap',
                                        assignment=testassignment, invalid=False)
        mommy.make('core.PointRangeToGrade',
                   point_to_grade_map=point_to_grade_map,
                   minimum_points=0,
                   maximum_points=10,
                   grade='Bad')
        mommy.make('core.PointRangeToGrade',
                   point_to_grade_map=point_to_grade_map,
                   minimum_points=11,
                   maximum_points=100,
                   grade='Good')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade.django.html',
                devilry_core_tags.devilry_grade(testassignment, 10)))
        self.assertTrue(selector.exists('.devilry-core-grade.devilry-core-grade-custom-table'))
        self.assertEqual(
            'Bad',
            selector.one('.devilry-core-grade').alltext_normalized)
