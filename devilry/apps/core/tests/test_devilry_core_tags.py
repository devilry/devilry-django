import htmls
from django.utils import timezone

from devilry.apps.core.models import Assignment, AssignmentGroup
from devilry.apps.core.templatetags import devilry_core_tags
from devilry.devilry_comment.models import Comment
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group.models import GroupComment
from django import test
from django.conf import settings
from django.template.loader import render_to_string
from model_bakery import baker


class TestDevilrySingleCandidateLongDisplayname(test.TestCase):
    def test_nonanonymous_cssclass(self):
        assignment = baker.make('core.Assignment')
        candidate = baker.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-candidate-long-displayname.django.html',
                devilry_core_tags.devilry_single_candidate_long_displayname(assignment, candidate, 'student')))
        self.assertTrue(selector.exists('.devilry-user-verbose-inline'))
        self.assertFalse(selector.exists('.devilry-core-candidate-anonymous-name'))

    def test_nonanonymous_without_fullname(self):
        assignment = baker.make('core.Assignment')
        candidate = baker.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-candidate-long-displayname.django.html',
                devilry_core_tags.devilry_single_candidate_long_displayname(assignment, candidate, 'student')))
        self.assertEqual('testuser',
                         selector.one('.devilry-user-verbose-inline').alltext_normalized)

    def test_nonanonymous_with_fullname(self):
        assignment = baker.make('core.Assignment')
        candidate = baker.make('core.Candidate',
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
        assignment = baker.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate = baker.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-candidate-long-displayname.django.html',
                devilry_core_tags.devilry_single_candidate_long_displayname(assignment, candidate, 'examiner')))
        self.assertFalse(selector.exists('.devilry-user-verbose-inline'))
        self.assertTrue(selector.exists('.devilry-core-candidate-anonymous-name'))

    def test_anonymous(self):
        assignment = baker.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate = baker.make('core.Candidate',
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
        assignment = baker.make('core.Assignment')
        candidate = baker.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-candidate-short-displayname.django.html',
                devilry_core_tags.devilry_single_candidate_short_displayname(assignment, candidate, 'student')))
        self.assertTrue(selector.exists('.devilry-core-candidate-shortname'))
        self.assertFalse(selector.exists('.devilry-core-candidate-anonymous-name'))

    def test_nonanonymous_without_fullname(self):
        assignment = baker.make('core.Assignment')
        candidate = baker.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-candidate-short-displayname.django.html',
                devilry_core_tags.devilry_single_candidate_short_displayname(assignment, candidate, 'student')))
        self.assertEqual('testuser',
                         selector.one('.devilry-core-candidate-shortname').alltext_normalized)

    def test_nonanonymous_with_fullname(self):
        assignment = baker.make('core.Assignment')
        candidate = baker.make('core.Candidate',
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
        assignment = baker.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate = baker.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-candidate-short-displayname.django.html',
                devilry_core_tags.devilry_single_candidate_short_displayname(assignment, candidate, 'examiner')))
        self.assertFalse(selector.exists('.devilry-core-candidate-shortname'))
        self.assertTrue(selector.exists('.devilry-core-candidate-anonymous-name'))

    def test_anonymous(self):
        assignment = baker.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate = baker.make('core.Candidate',
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
        assignment = baker.make('core.Assignment')
        examiner = baker.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-examiner-long-displayname.django.html',
                devilry_core_tags.devilry_single_examiner_long_displayname(assignment, examiner, 'examiner')))
        self.assertTrue(selector.exists('.devilry-user-verbose-inline'))
        self.assertFalse(selector.exists('.devilry-core-examiner-anonymous-name'))

    def test_nonanonymous_without_fullname(self):
        assignment = baker.make('core.Assignment')
        examiner = baker.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-examiner-long-displayname.django.html',
                devilry_core_tags.devilry_single_examiner_long_displayname(assignment, examiner, 'examiner')))
        self.assertEqual('testuser',
                         selector.one('.devilry-user-verbose-inline').alltext_normalized)

    def test_nonanonymous_with_fullname(self):
        assignment = baker.make('core.Assignment')
        examiner = baker.make('core.Examiner',
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
        assignment = baker.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        examiner = baker.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-examiner-long-displayname.django.html',
                devilry_core_tags.devilry_single_examiner_long_displayname(assignment, examiner, 'student')))
        self.assertFalse(selector.exists('.devilry-user-verbose-inline'))
        self.assertTrue(selector.exists('.devilry-core-examiner-anonymous-name'))

    def test_anonymous(self):
        assignment = baker.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        examiner = baker.make('core.Examiner',
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
        assignment = baker.make('core.Assignment')
        examiner = baker.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-examiner-short-displayname.django.html',
                devilry_core_tags.devilry_single_examiner_short_displayname(assignment, examiner, 'examiner')))
        self.assertTrue(selector.exists('.devilry-core-examiner-shortname'))
        self.assertFalse(selector.exists('.devilry-core-examiner-anonymous-name'))

    def test_nonanonymous_without_fullname(self):
        assignment = baker.make('core.Assignment')
        examiner = baker.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-examiner-short-displayname.django.html',
                devilry_core_tags.devilry_single_examiner_short_displayname(assignment, examiner, 'examiner')))
        self.assertEqual('testuser',
                         selector.one('.devilry-core-examiner-shortname').alltext_normalized)

    def test_nonanonymous_with_fullname(self):
        assignment = baker.make('core.Assignment')
        examiner = baker.make('core.Examiner',
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
        assignment = baker.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        examiner = baker.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/single-examiner-short-displayname.django.html',
                devilry_core_tags.devilry_single_examiner_short_displayname(assignment, examiner, 'student')))
        self.assertFalse(selector.exists('.devilry-core-examiner-shortname'))
        self.assertTrue(selector.exists('.devilry-core-examiner-anonymous-name'))

    def test_anonymous(self):
        assignment = baker.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        examiner = baker.make('core.Examiner',
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
        assignment = baker.make('core.Assignment')
        candidate = baker.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_long_displayname(assignment, [candidate], 'student')))
        self.assertTrue(selector.exists('.devilry-user-verbose-inline'))
        self.assertFalse(selector.exists('.devilry-core-candidate-anonymous-name'))

    def test_empty(self):
        assignment = baker.make('core.Assignment')
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
        assignment = baker.make('core.Assignment')
        candidate = baker.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_long_displayname(assignment, [candidate], 'student')))
        self.assertEqual('testuser',
                         selector.one('.devilry-user-verbose-inline').alltext_normalized)

    def test_nonanonymous_with_fullname(self):
        assignment = baker.make('core.Assignment')
        candidate = baker.make('core.Candidate',
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
        assignment = baker.make('core.Assignment')
        candidate1 = baker.make('core.Candidate',
                                assignment_group__parentnode=assignment,
                                relatedstudent__user__shortname='testuser1')
        candidate2 = baker.make('core.Candidate',
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
        assignment = baker.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate = baker.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_long_displayname(assignment, [candidate], 'examiner')))
        self.assertFalse(selector.exists('.devilry-user-verbose-inline'))
        self.assertTrue(selector.exists('.devilry-core-candidate-anonymous-name'))

    def test_anonymous(self):
        assignment = baker.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate = baker.make('core.Candidate',
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
        assignment = baker.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        candidate1 = baker.make('core.Candidate',
                                assignment_group__parentnode=assignment,
                                relatedstudent__automatic_anonymous_id='MyAnonymousId1',
                                relatedstudent__user__shortname='testuser1')
        candidate2 = baker.make('core.Candidate',
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
        assignment = baker.make('core.Assignment')
        candidate = baker.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_short_displayname(assignment, [candidate], 'student')))
        self.assertTrue(selector.exists('.devilry-core-candidate-shortname'))
        self.assertFalse(selector.exists('.devilry-core-candidate-anonymous-name'))

    def test_empty(self):
        assignment = baker.make('core.Assignment')
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
        assignment = baker.make('core.Assignment')
        candidate = baker.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_short_displayname(assignment, [candidate], 'student')))
        self.assertEqual('testuser',
                         selector.one('.devilry-core-candidate-shortname').alltext_normalized)

    def test_nonanonymous_with_fullname(self):
        assignment = baker.make('core.Assignment')
        candidate = baker.make('core.Candidate',
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
        assignment = baker.make('core.Assignment')
        candidate1 = baker.make('core.Candidate',
                                assignment_group__parentnode=assignment,
                                relatedstudent__user__shortname='testuser1')
        candidate2 = baker.make('core.Candidate',
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
        assignment = baker.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate = baker.make('core.Candidate',
                               assignment_group__parentnode=assignment,
                               relatedstudent__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-candidates-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_candidates_short_displayname(assignment, [candidate], 'examiner')))
        self.assertFalse(selector.exists('.devilry-core-candidate-shortname'))
        self.assertTrue(selector.exists('.devilry-core-candidate-anonymous-name'))

    def test_anonymous(self):
        assignment = baker.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        candidate = baker.make('core.Candidate',
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
        assignment = baker.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        candidate1 = baker.make('core.Candidate',
                                assignment_group__parentnode=assignment,
                                relatedstudent__automatic_anonymous_id='MyAnonymousId1',
                                relatedstudent__user__shortname='testuser1')
        candidate2 = baker.make('core.Candidate',
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
        assignment = baker.make('core.Assignment')
        examiner = baker.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_long_displayname(assignment, [examiner], 'examiner')))
        self.assertTrue(selector.exists('.devilry-user-verbose-inline'))
        self.assertFalse(selector.exists('.devilry-core-examiner-anonymous-name'))

    def test_empty(self):
        assignment = baker.make('core.Assignment')
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
        assignment = baker.make('core.Assignment')
        examiner = baker.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_long_displayname(assignment, [examiner], 'examiner')))
        self.assertEqual('testuser',
                         selector.one('.devilry-user-verbose-inline').alltext_normalized)

    def test_nonanonymous_multiple_examiners(self):
        assignment = baker.make('core.Assignment')
        examiner1 = baker.make('core.Examiner',
                               assignment_group__parentnode=assignment,
                               relatedexaminer__user__shortname='testuser1')
        examiner2 = baker.make('core.Examiner',
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
        assignment = baker.make('core.Assignment')
        examiner = baker.make('core.Examiner',
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
        assignment = baker.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        examiner = baker.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-long-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_long_displayname(assignment, [examiner], 'student')))
        self.assertFalse(selector.exists('.devilry-user-verbose-inline'))
        self.assertTrue(selector.exists('.devilry-core-examiner-anonymous-name'))

    def test_anonymous(self):
        assignment = baker.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        examiner = baker.make('core.Examiner',
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
        assignment = baker.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        examiner1 = baker.make('core.Examiner',
                               assignment_group__parentnode=assignment,
                               relatedexaminer__automatic_anonymous_id='MyAnonymousId1',
                               relatedexaminer__user__shortname='testuser1')
        examiner2 = baker.make('core.Examiner',
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
        assignment = baker.make('core.Assignment')
        examiner = baker.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_short_displayname(assignment, [examiner], 'examiner')))
        self.assertTrue(selector.exists('.devilry-core-examiner-shortname'))
        self.assertFalse(selector.exists('.devilry-core-examiner-anonymous-name'))

    def test_empty(self):
        assignment = baker.make('core.Assignment')
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
        assignment = baker.make('core.Assignment')
        examiner = baker.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_short_displayname(assignment, [examiner], 'examiner')))
        self.assertEqual('testuser',
                         selector.one('.devilry-core-examiner-shortname').alltext_normalized)

    def test_nonanonymous_with_fullname(self):
        assignment = baker.make('core.Assignment')
        examiner = baker.make('core.Examiner',
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
        assignment = baker.make('core.Assignment')
        examiner1 = baker.make('core.Examiner',
                               assignment_group__parentnode=assignment,
                               relatedexaminer__user__shortname='testuser1')
        examiner2 = baker.make('core.Examiner',
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
        assignment = baker.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        examiner = baker.make('core.Examiner',
                              assignmentgroup__parentnode=assignment,
                              relatedexaminer__user__shortname='testuser')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/multiple-examiners-short-displayname.django.html',
                devilry_core_tags.devilry_multiple_examiners_short_displayname(assignment, [examiner], 'student')))
        self.assertFalse(selector.exists('.devilry-core-examiner-shortname'))
        self.assertTrue(selector.exists('.devilry-core-examiner-anonymous-name'))

    def test_anonymous(self):
        assignment = baker.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        examiner = baker.make('core.Examiner',
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
        assignment = baker.make('core.Assignment',
                                anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        examiner1 = baker.make('core.Examiner',
                               assignment_group__parentnode=assignment,
                               relatedexaminer__automatic_anonymous_id='MyAnonymousId1',
                               relatedexaminer__user__shortname='testuser1')
        examiner2 = baker.make('core.Examiner',
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


class TestDevilryGradeShort(test.TestCase):
    def test_failed(self):
        testassignment = baker.make(
            'core.Assignment',
            passing_grade_min_points=1,
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-short.django.html',
                devilry_core_tags.devilry_grade_short(testassignment, 0)))
        self.assertTrue(selector.exists(
            '.devilry-core-grade-short.devilry-core-grade-failed'))

    def test_passed(self):
        testassignment = baker.make(
            'core.Assignment',
            passing_grade_min_points=1,
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-short.django.html',
                devilry_core_tags.devilry_grade_short(testassignment, 1)))
        self.assertTrue(selector.exists(
            '.devilry-core-grade-short.devilry-core-grade-passed'))

    def test_passed_failed_failed(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-short.django.html',
                devilry_core_tags.devilry_grade_short(testassignment, 0)))
        self.assertTrue(selector.exists(
            '.devilry-core-grade-short.devilry-core-grade.devilry-core-grade-mapper-passed-failed'))
        self.assertEqual(
            'failed',
            selector.one('.devilry-core-grade').alltext_normalized)

    def test_passed_failed_passed(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-short.django.html',
                devilry_core_tags.devilry_grade_short(testassignment, 10)))
        self.assertTrue(selector.exists(
            '.devilry-core-grade-short.devilry-core-grade.devilry-core-grade-mapper-passed-failed'))
        self.assertEqual(
            'passed',
            selector.one('.devilry-core-grade').alltext_normalized)

    def test_raw_points(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS,
            max_points=100)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-short.django.html',
                devilry_core_tags.devilry_grade_short(testassignment, 10)))
        self.assertTrue(selector.exists(
            '.devilry-core-grade-short.devilry-core-grade.devilry-core-grade-mapper-raw-points'))
        self.assertEqual(
            '10/100',
            selector.one('.devilry-core-grade').alltext_normalized)

    def test_custom_table(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE)
        point_to_grade_map = baker.make('core.PointToGradeMap',
                                        assignment=testassignment, invalid=False)
        baker.make('core.PointRangeToGrade',
                   point_to_grade_map=point_to_grade_map,
                   minimum_points=0,
                   maximum_points=10,
                   grade='Bad')
        baker.make('core.PointRangeToGrade',
                   point_to_grade_map=point_to_grade_map,
                   minimum_points=11,
                   maximum_points=100,
                   grade='Good')
        prefetched_assignment = Assignment.objects.prefetch_point_to_grade_map().get(id=testassignment.id)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-short.django.html',
                devilry_core_tags.devilry_grade_short(prefetched_assignment, 10)))
        self.assertTrue(selector.exists(
            '.devilry-core-grade-short.devilry-core-grade.devilry-core-grade-mapper-custom-table'))
        self.assertEqual(
            'Bad',
            selector.one('.devilry-core-grade').alltext_normalized)


class TestDevilryGradeFull(test.TestCase):
    def test_failed(self):
        testassignment = baker.make(
            'core.Assignment',
            passing_grade_min_points=1,
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-full.django.html',
                devilry_core_tags.devilry_grade_full(testassignment, 0, "student")))
        self.assertTrue(selector.exists(
            '.devilry-core-grade-full.devilry-core-grade-failed'))

    def test_passed(self):
        testassignment = baker.make(
            'core.Assignment',
            passing_grade_min_points=1,
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-full.django.html',
                devilry_core_tags.devilry_grade_full(testassignment, 1, "student")))
        self.assertTrue(selector.exists(
            '.devilry-core-grade-full.devilry-core-grade-passed'))

    def test_passed_failed_failed(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-full.django.html',
                devilry_core_tags.devilry_grade_full(testassignment, 0, "student")))
        self.assertTrue(selector.exists(
            '.devilry-core-grade-full.devilry-core-grade.devilry-core-grade-mapper-passed-failed'))
        self.assertEqual(
            'failed',
            selector.one('.devilry-core-grade .devilry-core-grade-main').alltext_normalized)

    def test_passed_failed_passed(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-full.django.html',
                devilry_core_tags.devilry_grade_full(testassignment, 10, "student")))
        self.assertTrue(selector.exists(
            '.devilry-core-grade-full.devilry-core-grade.devilry-core-grade-mapper-passed-failed'))
        self.assertEqual(
            'passed',
            selector.one('.devilry-core-grade .devilry-core-grade-main').alltext_normalized)

    def test_raw_points(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS,
            max_points=100)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-full.django.html',
                devilry_core_tags.devilry_grade_full(testassignment, 10, "student")))
        self.assertTrue(selector.exists(
            '.devilry-core-grade-full.devilry-core-grade.devilry-core-grade-mapper-raw-points'))
        self.assertEqual(
            '10/100',
            selector.one('.devilry-core-grade .devilry-core-grade-main').alltext_normalized)

    def test_custom_table(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE)
        point_to_grade_map = baker.make('core.PointToGradeMap',
                                        assignment=testassignment, invalid=False)
        baker.make('core.PointRangeToGrade',
                   point_to_grade_map=point_to_grade_map,
                   minimum_points=0,
                   maximum_points=10,
                   grade='Bad')
        baker.make('core.PointRangeToGrade',
                   point_to_grade_map=point_to_grade_map,
                   minimum_points=11,
                   maximum_points=100,
                   grade='Good')
        prefetched_assignment = Assignment.objects.prefetch_point_to_grade_map().get(id=testassignment.id)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-full.django.html',
                devilry_core_tags.devilry_grade_full(prefetched_assignment, 10, "student")))
        self.assertTrue(selector.exists(
            '.devilry-core-grade-full.devilry-core-grade.devilry-core-grade-mapper-custom-table'))
        self.assertEqual(
            'Bad',
            selector.one('.devilry-core-grade .devilry-core-grade-main').alltext_normalized)

    def test_details_students_can_see_points_false(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED,
            students_can_see_points=False,
            max_points=10)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-full.django.html',
                devilry_core_tags.devilry_grade_full(testassignment, 8, "student")))
        self.assertFalse(selector.exists('.devilry-core-grade-details-points'))

    def test_details_students_can_see_points_false_not_student(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED,
            students_can_see_points=False,
            max_points=10)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-full.django.html',
                devilry_core_tags.devilry_grade_full(testassignment, 8, "examiner")))
        self.assertEqual(
            '8/10',
            selector.one('.devilry-core-grade-details-points').alltext_normalized)

    def test_details_students_can_see_points_true(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED,
            students_can_see_points=True,
            max_points=10)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-full.django.html',
                devilry_core_tags.devilry_grade_full(testassignment, 8, "student")))
        self.assertEqual(
            '8/10',
            selector.one('.devilry-core-grade-details-points').alltext_normalized)

    def test_details_students_can_see_points_true_mapper_raw_points(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS,
            students_can_see_points=True,
            max_points=10)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-full.django.html',
                devilry_core_tags.devilry_grade_full(testassignment, 8, "student")))
        self.assertFalse(selector.exists('.devilry-core-grade-details-points'))

    def test_details_is_passing_grade_mapper_passedfailed(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-full.django.html',
                devilry_core_tags.devilry_grade_full(testassignment, 8, "student")))
        self.assertFalse(selector.exists('.devilry-core-grade-details-is-passing-grade'))

    def test_details_is_passing_grade_true(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS,
            passing_grade_min_points=1)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-full.django.html',
                devilry_core_tags.devilry_grade_full(testassignment, 8, "student")))
        self.assertEqual(
            'passed',
            selector.one('.devilry-core-grade-details-is-passing-grade').alltext_normalized)

    def test_details_is_passing_grade_false(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS,
            passing_grade_min_points=1)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-full.django.html',
                devilry_core_tags.devilry_grade_full(testassignment, 0, "student")))
        self.assertEqual(
            'failed',
            selector.one('.devilry-core-grade-details-is-passing-grade').alltext_normalized)

    def test_passedfailed_grade_sanitycheck_students_can_see_points_true(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED,
            students_can_see_points=True,
            passing_grade_min_points=1,
            max_points=10)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-full.django.html',
                devilry_core_tags.devilry_grade_full(testassignment, 5, "student")))
        self.assertEqual(
            'passed (5/10)',
            selector.one('.devilry-core-grade').alltext_normalized)

    def test_rawpoints_grade_sanitycheck_students_can_see_points_true(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS,
            students_can_see_points=True,
            passing_grade_min_points=1,
            max_points=10)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-full.django.html',
                devilry_core_tags.devilry_grade_full(testassignment, 5, "student")))
        self.assertEqual(
            '5/10 (passed)',
            selector.one('.devilry-core-grade').alltext_normalized)

    def test_custom_table_full_grade_sanitycheck_students_can_see_points_true(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE,
            passing_grade_min_points=1,
            students_can_see_points=True,
            max_points=10)
        point_to_grade_map = baker.make('core.PointToGradeMap',
                                        assignment=testassignment, invalid=False)
        baker.make('core.PointRangeToGrade',
                   point_to_grade_map=point_to_grade_map,
                   minimum_points=0,
                   maximum_points=10,
                   grade='Bad')
        prefetched_assignment = Assignment.objects.prefetch_point_to_grade_map().get(id=testassignment.id)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-full.django.html',
                devilry_core_tags.devilry_grade_full(prefetched_assignment, 5, "student")))
        self.assertTrue(selector.exists(
            '.devilry-core-grade-full.devilry-core-grade.devilry-core-grade-mapper-custom-table'))
        self.assertEqual(
            'Bad (passed - 5/10)',
            selector.one('.devilry-core-grade').alltext_normalized)

    def test_passedfailed_grade_sanitycheck_students_can_see_points_false_student(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED,
            students_can_see_points=False,
            passing_grade_min_points=1,
            max_points=10)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-full.django.html',
                devilry_core_tags.devilry_grade_full(testassignment, 5, "student")))
        self.assertEqual(
            'passed',
            selector.one('.devilry-core-grade').alltext_normalized)

    def test_rawpoints_grade_sanitycheck_students_can_see_points_false_student(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS,
            students_can_see_points=False,
            passing_grade_min_points=1,
            max_points=10)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-full.django.html',
                devilry_core_tags.devilry_grade_full(testassignment, 5, "student")))
        self.assertEqual(
            '5/10 (passed)',
            selector.one('.devilry-core-grade').alltext_normalized)

    def test_custom_table_full_grade_sanitycheck_students_can_see_points_false_student(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE,
            passing_grade_min_points=1,
            students_can_see_points=False,
            max_points=10)
        point_to_grade_map = baker.make('core.PointToGradeMap',
                                        assignment=testassignment, invalid=False)
        baker.make('core.PointRangeToGrade',
                   point_to_grade_map=point_to_grade_map,
                   minimum_points=0,
                   maximum_points=10,
                   grade='Bad')
        prefetched_assignment = Assignment.objects.prefetch_point_to_grade_map().get(id=testassignment.id)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-full.django.html',
                devilry_core_tags.devilry_grade_full(prefetched_assignment, 5, "student")))
        self.assertTrue(selector.exists(
            '.devilry-core-grade-full.devilry-core-grade.devilry-core-grade-mapper-custom-table'))
        self.assertEqual(
            'Bad (passed)',
            selector.one('.devilry-core-grade').alltext_normalized)

    def test_passedfailed_grade_sanitycheck_students_can_see_points_false_not_student(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED,
            students_can_see_points=False,
            passing_grade_min_points=1,
            max_points=10)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-full.django.html',
                devilry_core_tags.devilry_grade_full(testassignment, 5, "examiner")))
        self.assertEqual(
            'passed (5/10)',
            selector.one('.devilry-core-grade').alltext_normalized)

    def test_rawpoints_grade_sanitycheck_students_can_see_points_false_not_student(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS,
            students_can_see_points=False,
            passing_grade_min_points=1,
            max_points=10)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-full.django.html',
                devilry_core_tags.devilry_grade_full(testassignment, 5, "examiner")))
        self.assertEqual(
            '5/10 (passed)',
            selector.one('.devilry-core-grade').alltext_normalized)

    def test_custom_table_full_grade_sanitycheck_students_can_see_points_false_not_student(self):
        testassignment = baker.make(
            'core.Assignment',
            points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE,
            passing_grade_min_points=1,
            students_can_see_points=False,
            max_points=10)
        point_to_grade_map = baker.make('core.PointToGradeMap',
                                        assignment=testassignment, invalid=False)
        baker.make('core.PointRangeToGrade',
                   point_to_grade_map=point_to_grade_map,
                   minimum_points=0,
                   maximum_points=10,
                   grade='Bad')
        prefetched_assignment = Assignment.objects.prefetch_point_to_grade_map().get(id=testassignment.id)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/grade-full.django.html',
                devilry_core_tags.devilry_grade_full(prefetched_assignment, 5, "examiner")))
        self.assertTrue(selector.exists(
            '.devilry-core-grade-full.devilry-core-grade.devilry-core-grade-mapper-custom-table'))
        self.assertEqual(
            'Bad (passed - 5/10)',
            selector.one('.devilry-core-grade').alltext_normalized)


class TestDevilryCommentSummary(test.TestCase):

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_zero_comments_from_students(self):
        testgroup = baker.make('core.AssignmentGroup')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/comment-summary.django.html',
                devilry_core_tags.devilry_comment_summary(testgroup)))
        self.assertEqual(
            '0 comments from student.',
            selector.one('.devilry-core-comment-summary-studentcomments').alltext_normalized)

    def test_one_comment_from_students(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup,
                   feedback_set__deadline_datetime=timezone.now(),
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   text='asd',
                   user_role=Comment.USER_ROLE_STUDENT)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/comment-summary.django.html',
                devilry_core_tags.devilry_comment_summary(testgroup)))
        self.assertEqual(
            '1 comment from student.',
            selector.one('.devilry-core-comment-summary-studentcomments').alltext_normalized)

    def test_multiple_comments_from_students(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup,
                   feedback_set__deadline_datetime=timezone.now(),
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   text='asd',
                   user_role=Comment.USER_ROLE_STUDENT)
        baker.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup,
                   feedback_set__deadline_datetime=timezone.now(),
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   text='asd',
                   user_role=Comment.USER_ROLE_STUDENT)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/comment-summary.django.html',
                devilry_core_tags.devilry_comment_summary(testgroup)))
        self.assertEqual(
            '2 comments from student.',
            selector.one('.devilry-core-comment-summary-studentcomments').alltext_normalized)

    def test_zero_commentfiles_from_students(self):
        testgroup = baker.make('core.AssignmentGroup')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/comment-summary.django.html',
                devilry_core_tags.devilry_comment_summary(testgroup)))
        self.assertEqual(
            '0 files from student.',
            selector.one('.devilry-core-comment-summary-studentfiles').alltext_normalized)

    def test_one_commentfile_from_students(self):
        AssignmentGroupDbCacheCustomSql().initialize()
        testgroup = baker.make('core.AssignmentGroup')
        testcomment = baker.make('devilry_group.GroupComment',
                                 feedback_set__group=testgroup,
                                 feedback_set__deadline_datetime=timezone.now(),
                                 comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                                 visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                                 user_role=Comment.USER_ROLE_STUDENT)
        baker.make('devilry_comment.CommentFile', comment=testcomment)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/comment-summary.django.html',
                devilry_core_tags.devilry_comment_summary(testgroup)))
        self.assertEqual(
            '1 file from student.',
            selector.one('.devilry-core-comment-summary-studentfiles').alltext_normalized)

    def test_multiple_commentfiles_from_students(self):
        testgroup = baker.make('core.AssignmentGroup')
        testcomment1 = baker.make('devilry_group.GroupComment',
                                  feedback_set__group=testgroup,
                                  feedback_set__deadline_datetime=timezone.now(),
                                  visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                                  comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                                  user_role=Comment.USER_ROLE_STUDENT)
        baker.make('devilry_comment.CommentFile', comment=testcomment1)
        testcomment2 = baker.make('devilry_group.GroupComment',
                                  feedback_set__group=testgroup,
                                  feedback_set__deadline_datetime=timezone.now(),
                                  visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                                  comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                                  user_role=Comment.USER_ROLE_STUDENT)
        baker.make('devilry_comment.CommentFile', comment=testcomment2)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/comment-summary.django.html',
                devilry_core_tags.devilry_comment_summary(testgroup)))
        self.assertEqual(
            '2 files from student.',
            selector.one('.devilry-core-comment-summary-studentfiles').alltext_normalized)

    def test_zero_comments_from_examiners(self):
        testgroup = baker.make('core.AssignmentGroup')
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/comment-summary.django.html',
                devilry_core_tags.devilry_comment_summary(testgroup)))
        self.assertEqual(
            '0 comments from examiner.',
            selector.one('.devilry-core-comment-summary-examinercomments').alltext_normalized)

    def test_one_comment_from_examiners(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup,
                   feedback_set__deadline_datetime=timezone.now(),
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user_role=Comment.USER_ROLE_EXAMINER)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/comment-summary.django.html',
                devilry_core_tags.devilry_comment_summary(testgroup)))
        self.assertEqual(
            '1 comment from examiner.',
            selector.one('.devilry-core-comment-summary-examinercomments').alltext_normalized)

    def test_multiple_comments_from_examiners(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup,
                   feedback_set__deadline_datetime=timezone.now(),
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user_role=Comment.USER_ROLE_EXAMINER)
        baker.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup,
                   feedback_set__deadline_datetime=timezone.now(),
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user_role=Comment.USER_ROLE_EXAMINER)
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/comment-summary.django.html',
                devilry_core_tags.devilry_comment_summary(testgroup)))
        self.assertEqual(
            '2 comments from examiner.',
            selector.one('.devilry-core-comment-summary-examinercomments').alltext_normalized)

    def test_zero_private_groupcomments_from_user(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.AssignmentGroup')
        testgroup = AssignmentGroup.objects\
            .annotate_with_number_of_private_groupcomments_from_user(user=testuser).first()
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/comment-summary.django.html',
                devilry_core_tags.devilry_comment_summary(testgroup)))
        self.assertFalse(selector.exists('.devilry-core-comment-summary-unpublishedcomments'))

    def test_one_private_groupcomments_from_user(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup,
                   feedback_set__deadline_datetime=timezone.now(),
                   visibility=GroupComment.VISIBILITY_PRIVATE,
                   user=testuser,
                   user_role=Comment.USER_ROLE_EXAMINER)
        testgroup = AssignmentGroup.objects\
            .annotate_with_number_of_private_groupcomments_from_user(user=testuser).first()
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/comment-summary.django.html',
                devilry_core_tags.devilry_comment_summary(testgroup)))
        self.assertEqual(
            '1 unpublished comment from you.',
            selector.one('.devilry-core-comment-summary-unpublishedcomments').alltext_normalized)

    def test_multiple_private_groupcomments_from_user(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup,
                   feedback_set__deadline_datetime=timezone.now(),
                   user=testuser,
                   visibility=GroupComment.VISIBILITY_PRIVATE,
                   user_role=Comment.USER_ROLE_EXAMINER)
        baker.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup,
                   feedback_set__deadline_datetime=timezone.now(),
                   user=testuser,
                   visibility=GroupComment.VISIBILITY_PRIVATE,
                   user_role=Comment.USER_ROLE_EXAMINER)
        testgroup = AssignmentGroup.objects\
            .annotate_with_number_of_private_groupcomments_from_user(user=testuser).first()
        selector = htmls.S(
            render_to_string(
                'devilry_core/templatetags/comment-summary.django.html',
                devilry_core_tags.devilry_comment_summary(testgroup)))
        self.assertEqual(
            '2 unpublished comments from you.',
            selector.one('.devilry-core-comment-summary-unpublishedcomments').alltext_normalized)
