import htmls
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
                devilry_core_tags.devilry_single_candidate_long_displayname(assignment, candidate)))
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
                devilry_core_tags.devilry_single_candidate_long_displayname(assignment, candidate)))
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
                devilry_core_tags.devilry_single_candidate_long_displayname(assignment, candidate)))
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
                devilry_core_tags.devilry_single_candidate_long_displayname(assignment, candidate)))
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
                devilry_core_tags.devilry_single_candidate_long_displayname(assignment, candidate)))
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
                devilry_core_tags.devilry_single_candidate_short_displayname(assignment, candidate)))
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
                devilry_core_tags.devilry_single_candidate_short_displayname(assignment, candidate)))
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
                devilry_core_tags.devilry_single_candidate_short_displayname(assignment, candidate)))
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
                devilry_core_tags.devilry_single_candidate_short_displayname(assignment, candidate)))
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
                devilry_core_tags.devilry_single_candidate_short_displayname(assignment, candidate)))
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
                devilry_core_tags.devilry_single_examiner_long_displayname(assignment, examiner)))
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
                devilry_core_tags.devilry_single_examiner_long_displayname(assignment, examiner)))
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
                devilry_core_tags.devilry_single_examiner_long_displayname(assignment, examiner)))
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
                devilry_core_tags.devilry_single_examiner_long_displayname(assignment, examiner)))
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
                devilry_core_tags.devilry_single_examiner_long_displayname(assignment, examiner)))
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
                devilry_core_tags.devilry_single_examiner_short_displayname(assignment, examiner)))
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
                devilry_core_tags.devilry_single_examiner_short_displayname(assignment, examiner)))
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
                devilry_core_tags.devilry_single_examiner_short_displayname(assignment, examiner)))
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
                devilry_core_tags.devilry_single_examiner_short_displayname(assignment, examiner)))
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
                devilry_core_tags.devilry_single_examiner_short_displayname(assignment, examiner)))
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
                devilry_core_tags.devilry_multiple_candidates_long_displayname(assignment, [candidate])))
        self.assertTrue(selector.exists('.devilry-user-verbose-inline'))
        self.assertFalse(selector.exists('.devilry-core-candidate-anonymous-name'))

    def test_empty(self):
        assignment = mommy.make('core.Assignment')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_long_displayname(assignment, [])))
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
                devilry_core_tags.devilry_multiple_candidates_long_displayname(assignment, [candidate])))
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
                devilry_core_tags.devilry_multiple_candidates_long_displayname(assignment, [candidate])))
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
                    assignment, [candidate1, candidate2])))
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
                devilry_core_tags.devilry_multiple_candidates_long_displayname(assignment, [candidate])))
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
                devilry_core_tags.devilry_multiple_candidates_long_displayname(assignment, [candidate])))
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
                    assignment, [candidate1, candidate2])))
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
                devilry_core_tags.devilry_multiple_candidates_short_displayname(assignment, [candidate])))
        self.assertTrue(selector.exists('.devilry-core-candidate-shortname'))
        self.assertFalse(selector.exists('.devilry-core-candidate-anonymous-name'))

    def test_empty(self):
        assignment = mommy.make('core.Assignment')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_short_displayname(assignment, [])))
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
                devilry_core_tags.devilry_multiple_candidates_short_displayname(assignment, [candidate])))
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
                devilry_core_tags.devilry_multiple_candidates_short_displayname(assignment, [candidate])))
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
                    assignment, [candidate1, candidate2])))
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
                devilry_core_tags.devilry_multiple_candidates_short_displayname(assignment, [candidate])))
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
                devilry_core_tags.devilry_multiple_candidates_short_displayname(assignment, [candidate])))
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
                    assignment, [candidate1, candidate2])))
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
                devilry_core_tags.devilry_multiple_examiners_long_displayname(assignment, [examiner])))
        self.assertTrue(selector.exists('.devilry-user-verbose-inline'))
        self.assertFalse(selector.exists('.devilry-core-examiner-anonymous-name'))

    def test_empty(self):
        assignment = mommy.make('core.Assignment')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_long_displayname(assignment, [])))
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
                devilry_core_tags.devilry_multiple_examiners_long_displayname(assignment, [examiner])))
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
                    assignment, [examiner1, examiner2])))
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
                devilry_core_tags.devilry_multiple_examiners_long_displayname(assignment, [examiner])))
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
                devilry_core_tags.devilry_multiple_examiners_long_displayname(assignment, [examiner])))
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
                devilry_core_tags.devilry_multiple_examiners_long_displayname(assignment, [examiner])))
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
                    assignment, [examiner1, examiner2])))
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
                devilry_core_tags.devilry_multiple_examiners_short_displayname(assignment, [examiner])))
        self.assertTrue(selector.exists('.devilry-core-examiner-shortname'))
        self.assertFalse(selector.exists('.devilry-core-examiner-anonymous-name'))

    def test_empty(self):
        assignment = mommy.make('core.Assignment')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_short_displayname(assignment, [])))
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
                devilry_core_tags.devilry_multiple_examiners_short_displayname(assignment, [examiner])))
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
                devilry_core_tags.devilry_multiple_examiners_short_displayname(assignment, [examiner])))
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
                    assignment, [examiner1, examiner2])))
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
                devilry_core_tags.devilry_multiple_examiners_short_displayname(assignment, [examiner])))
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
                devilry_core_tags.devilry_multiple_examiners_short_displayname(assignment, [examiner])))
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
                    assignment, [examiner1, examiner2])))
        names = [element.alltext_normalized
                 for element in selector.list('.devilry-core-examiner-anonymous-name')]
        self.assertEqual(['MyAnonymousId1', 'MyAnonymousId2'], names)
