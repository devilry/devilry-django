from django.db import IntegrityError

from django.test import TestCase
from model_mommy import mommy

from devilry.project.develop.testhelpers.corebuilder import UserBuilder2


class TestRelatedStudentModel(TestCase):
    def test_unique_in_period(self):
        testperiod = mommy.make('core.Period')
        testuser = UserBuilder2().user
        mommy.make('core.RelatedStudent', period=testperiod, user=testuser)
        with self.assertRaises(IntegrityError):
            mommy.make('core.RelatedStudent', period=testperiod, user=testuser)


class TestRelatedExaminerModel(TestCase):
    def test_unique_in_period(self):
        testperiod = mommy.make('core.Period')
        testuser = UserBuilder2().user
        mommy.make('core.RelatedExaminer', period=testperiod, user=testuser)
        with self.assertRaises(IntegrityError):
            mommy.make('core.RelatedExaminer', period=testperiod, user=testuser)


class TestRelatedStudentSyncSystemTag(TestCase):
    def test_tag_unique_for_relatedstudent(self):
        testrelatedstudent = mommy.make('core.RelatedStudent')
        mommy.make('core.RelatedStudentSyncSystemTag', tag='testtag',
                   relatedstudent=testrelatedstudent)
        with self.assertRaises(IntegrityError):
            mommy.make('core.RelatedStudentSyncSystemTag', tag='testtag',
                       relatedstudent=testrelatedstudent)


class TestRelatedExaminerSyncSystemTag(TestCase):
    def test_tag_unique_for_relatedexaminer(self):
        testrelatedexaminer = mommy.make('core.RelatedExaminer')
        mommy.make('core.RelatedExaminerSyncSystemTag', tag='testtag',
                   relatedexaminer=testrelatedexaminer)
        with self.assertRaises(IntegrityError):
            mommy.make('core.RelatedExaminerSyncSystemTag', tag='testtag',
                       relatedexaminer=testrelatedexaminer)
