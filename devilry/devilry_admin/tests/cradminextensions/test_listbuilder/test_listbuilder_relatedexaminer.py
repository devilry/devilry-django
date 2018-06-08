import htmls
from django import test
from model_mommy import mommy

from devilry.apps.core.models import RelatedExaminer
from devilry.devilry_admin.cradminextensions.listbuilder import listbuilder_relatedexaminer
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestOnPeriodItemValue(test.TestCase):
    def test_title_without_fullname(self):
        relatedstudent = mommy.make('core.RelatedExaminer',
                                    user__shortname='test@example.com',
                                    user__fullname='')
        selector = htmls.S(listbuilder_relatedexaminer.OnPeriodItemValue(value=relatedstudent).render())
        self.assertEqual(
            'test@example.com',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_title_with_fullname(self):
        relatedstudent = mommy.make('core.RelatedExaminer',
                                    user__fullname='Test User',
                                    user__shortname='test@example.com')
        selector = htmls.S(listbuilder_relatedexaminer.OnPeriodItemValue(value=relatedstudent).render())
        self.assertEqual(
            'Test User',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_description_without_fullname(self):
        relatedstudent = mommy.make('core.RelatedExaminer',
                                    user__shortname='test@example.com',
                                    user__fullname='')
        selector = htmls.S(listbuilder_relatedexaminer.OnPeriodItemValue(value=relatedstudent).render())
        self.assertFalse(
            selector.exists('.django-cradmin-listbuilder-itemvalue-titledescription-description'))

    def test_description_with_fullname(self):
        relatedstudent = mommy.make('core.RelatedExaminer',
                                    user__fullname='Test User',
                                    user__shortname='test@example.com')
        selector = htmls.S(listbuilder_relatedexaminer.OnPeriodItemValue(value=relatedstudent).render())
        self.assertEqual(
            'test@example.com',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-description').alltext_normalized)


class TestOnassignmentItemValue(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __annotate_relatedexaminer(self, relatedexaminer, assignment):
        return RelatedExaminer.objects\
            .annotate_with_number_of_groups_on_assignment(assignment=assignment)\
            .extra_annotate_with_number_of_candidates_on_assignment(assignment=assignment)\
            .get(id=relatedexaminer.id)

    def test_title_without_fullname(self):
        relatedexaminer = mommy.make('core.RelatedExaminer',
                                     user__shortname='test@example.com',
                                     user__fullname='')
        testassignment = mommy.make('core.Assignment')
        relatedexaminer = self.__annotate_relatedexaminer(relatedexaminer, assignment=testassignment)
        selector = htmls.S(listbuilder_relatedexaminer.OnassignmentItemValue(value=relatedexaminer).render())
        self.assertEqual(
            'test@example.com',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_title_with_fullname(self):
        relatedexaminer = mommy.make('core.RelatedExaminer',
                                     user__fullname='Test User',
                                     user__shortname='test@example.com')
        testassignment = mommy.make('core.Assignment')
        relatedexaminer = self.__annotate_relatedexaminer(relatedexaminer, assignment=testassignment)
        selector = htmls.S(listbuilder_relatedexaminer.OnassignmentItemValue(value=relatedexaminer).render())
        self.assertEqual(
            'Test User(test@example.com)',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_summary_no_groups(self):
        relatedexaminer = mommy.make('core.RelatedExaminer')
        testassignment = mommy.make('core.Assignment')
        relatedexaminer = self.__annotate_relatedexaminer(relatedexaminer, assignment=testassignment)
        selector = htmls.S(listbuilder_relatedexaminer.OnassignmentItemValue(value=relatedexaminer).render())
        self.assertEqual(
            'No students',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-description').alltext_normalized)

    def test_summary_single_groups_no_projectgroups(self):
        relatedexaminer = mommy.make('core.RelatedExaminer')
        testassignment = mommy.make('core.Assignment')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer=relatedexaminer)
        mommy.make('core.Candidate',
                   assignment_group=testgroup)
        relatedexaminer = self.__annotate_relatedexaminer(relatedexaminer, assignment=testassignment)
        selector = htmls.S(listbuilder_relatedexaminer.OnassignmentItemValue(value=relatedexaminer).render())
        self.assertEqual(
            '1 student',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-description').alltext_normalized)

    def test_summary_multiple_groups_no_projectgroups(self):
        relatedexaminer = mommy.make('core.RelatedExaminer')
        testassignment = mommy.make('core.Assignment')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup1,
                   relatedexaminer=relatedexaminer)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup2,
                   relatedexaminer=relatedexaminer)
        mommy.make('core.Candidate',
                   assignment_group=testgroup2)
        relatedexaminer = self.__annotate_relatedexaminer(relatedexaminer, assignment=testassignment)
        selector = htmls.S(listbuilder_relatedexaminer.OnassignmentItemValue(value=relatedexaminer).render())
        self.assertEqual(
            '2 students',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-description').alltext_normalized)

    def test_summary_multiple_groups_with_multiple_candidates(self):
        relatedexaminer = mommy.make('core.RelatedExaminer')
        testassignment = mommy.make('core.Assignment')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup1,
                   relatedexaminer=relatedexaminer)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup2,
                   relatedexaminer=relatedexaminer)
        mommy.make('core.Candidate',
                   assignment_group=testgroup2)
        relatedexaminer = self.__annotate_relatedexaminer(relatedexaminer, assignment=testassignment)
        selector = htmls.S(listbuilder_relatedexaminer.OnassignmentItemValue(value=relatedexaminer).render())
        self.assertEqual(
            '3 students in 2 project groups',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-description').alltext_normalized)

    def test_summary_single_group_with_multiple_candidates(self):
        relatedexaminer = mommy.make('core.RelatedExaminer')
        testassignment = mommy.make('core.Assignment')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer=relatedexaminer)
        mommy.make('core.Candidate',
                   assignment_group=testgroup)
        mommy.make('core.Candidate',
                   assignment_group=testgroup)
        relatedexaminer = self.__annotate_relatedexaminer(relatedexaminer, assignment=testassignment)
        selector = htmls.S(listbuilder_relatedexaminer.OnassignmentItemValue(value=relatedexaminer).render())
        self.assertEqual(
            '2 students in 1 project group',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-description').alltext_normalized)
