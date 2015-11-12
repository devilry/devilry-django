from django.test import TestCase
import htmls
from model_mommy import mommy
from devilry.devilry_admin.listbuilder import assignmentgroup_listbuilder


class TestValue(TestCase):
    def test_render_candidate_fullnames_no_candidates(self):
        testgroup = mommy.make('core.AssignmentGroup')
        selector = htmls.S(assignmentgroup_listbuilder.Value(testgroup).render())
        self.assertEqual(
            'AssignmentGroup #{}'.format(testgroup.id),
            selector.one('.devilry-admin-assignmentgroup-listbuilder-candidate-fullnames').alltext_normalized)

    def test_render_candidate_fullnames_single_candidate(self):
        testgroup = mommy.make('core.AssignmentGroup', name='Testname')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test Candidate One')
        selector = htmls.S(assignmentgroup_listbuilder.Value(testgroup).render())
        self.assertEqual(
            'Test Candidate One',
            selector.one('.devilry-admin-assignmentgroup-listbuilder-candidate-fullnames').alltext_normalized)

    def test_render_candidate_fullnames_multiple_candidates(self):
        testgroup = mommy.make('core.AssignmentGroup', name='Testname')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test Candidate One')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test Candidate Two')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test Candidate Three')
        selector = htmls.S(assignmentgroup_listbuilder.Value(testgroup).render())
        fullnames = selector.one('.devilry-admin-assignmentgroup-listbuilder-candidate-fullnames')\
            .alltext_normalized.split(', ')
        self.assertEqual(
            {'Test Candidate One', 'Test Candidate Two', 'Test Candidate Three'},
            set(fullnames))

    def test_render_no_name(self):
        testgroup = mommy.make('core.AssignmentGroup', name='')
        selector = htmls.S(assignmentgroup_listbuilder.Value(testgroup).render())
        self.assertFalse(
            selector.exists('.devilry-admin-assignmentgroup-listbuilder-name'))

    def test_render_name(self):
        testgroup = mommy.make('core.AssignmentGroup', name='Testname')
        selector = htmls.S(assignmentgroup_listbuilder.Value(testgroup).render())
        self.assertEqual(
            'Testname',
            selector.one('.devilry-admin-assignmentgroup-listbuilder-name').alltext_normalized)

    def test_render_candidate_shortnames_no_candidates(self):
        testgroup = mommy.make('core.AssignmentGroup')
        selector = htmls.S(assignmentgroup_listbuilder.Value(testgroup).render())
        self.assertFalse(
            selector.exists('.devilry-admin-assignmentgroup-listbuilder-candidate-shortnames'))

    def test_render_candidate_shortnames_single_candidate(self):
        testgroup = mommy.make('core.AssignmentGroup', name='Testname')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='testcandidate1')
        selector = htmls.S(assignmentgroup_listbuilder.Value(testgroup).render())
        self.assertEqual(
            'testcandidate1',
            selector.one('.devilry-admin-assignmentgroup-listbuilder-candidate-shortnames').alltext_normalized)

    def test_render_candidate_shortnames_multiple_candidates(self):
        testgroup = mommy.make('core.AssignmentGroup', name='Testname')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='testcandidate1')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='testcandidate2')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='testcandidate3')
        selector = htmls.S(assignmentgroup_listbuilder.Value(testgroup).render())
        shortnames = selector.one('.devilry-admin-assignmentgroup-listbuilder-candidate-shortnames')\
            .alltext_normalized.split(', ')
        self.assertEqual(
            {'testcandidate1', 'testcandidate2', 'testcandidate3'},
            set(shortnames))

    def test_render_examiner_shortnames_no_examiners(self):
        testgroup = mommy.make('core.AssignmentGroup')
        selector = htmls.S(assignmentgroup_listbuilder.Value(testgroup).render())
        self.assertEqual(
            'No examiner(s)',
            selector.one('.devilry-admin-assignmentgroup-listbuilder-examiners'
                         ' .text-warning').alltext_normalized)

    def test_render_examiner_shortnames_single_examiner_without_fullname(self):
        testgroup = mommy.make('core.AssignmentGroup', name='Testname')
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__shortname='testexaminer1')
        selector = htmls.S(assignmentgroup_listbuilder.Value(testgroup).render())
        self.assertEqual(
            'testexaminer1',
            selector.one('.devilry-admin-assignmentgroup-listbuilder-examiners-list').alltext_normalized)

    def test_render_examiner_shortnames_single_examiner_with_fullname(self):
        testgroup = mommy.make('core.AssignmentGroup', name='Testname')
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__shortname='testexaminer1',
                   relatedexaminer__user__fullname='Test Examiner One')
        selector = htmls.S(assignmentgroup_listbuilder.Value(testgroup).render())
        self.assertEqual(
            'Test Examiner One(testexaminer1)',
            selector.one('.devilry-admin-assignmentgroup-listbuilder-examiners-list').alltext_normalized)

    def test_render_examiner_shortnames_multiple_examiners(self):
        testgroup = mommy.make('core.AssignmentGroup', name='Testname')
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__shortname='testexaminer1')
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__shortname='testexaminer2')
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer__user__shortname='testexaminer3')
        selector = htmls.S(assignmentgroup_listbuilder.Value(testgroup).render())
        shortnames = [name.strip() for name in
                      selector.one('.devilry-admin-assignmentgroup-listbuilder-examiners-list')
                      .alltext_normalized.split(', ')]
        self.assertEqual(
            {'testexaminer1', 'testexaminer2', 'testexaminer3'},
            set(shortnames))
