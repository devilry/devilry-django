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
