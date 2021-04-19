# -*- coding: utf-8 -*-


import htmls
from django import test
from django.conf import settings
from cradmin_legacy import datetimeutils
from model_bakery import baker

from devilry.apps.core.models import Period
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_qualifiesforexam.models import Status


class TestAdminItemValue(test.TestCase):
    def test_custom_cssclass(self):
        testperiod = baker.make('core.Period')
        selector = htmls.S(devilry_listbuilder.period.AdminItemValue(value=testperiod).render())
        self.assertTrue(selector.exists('.devilry-cradmin-perioditemvalue-admin'))

    def test_title(self):
        testperiod = baker.make('core.Period', long_name='Test Period')
        selector = htmls.S(devilry_listbuilder.period.AdminItemValue(value=testperiod).render())
        self.assertEqual(
                'Test Period',
                selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_description(self):
        testperiod = baker.make('core.Period',
                                start_time=datetimeutils.default_timezone_datetime(2015, 1, 15),
                                end_time=datetimeutils.default_timezone_datetime(2015, 12, 24))
        selector = htmls.S(devilry_listbuilder.period.AdminItemValue(value=testperiod).render())
        self.assertEqual(
                'Thursday January 15, 2015, 00:00 \u2014 Thursday December 24, 2015, 00:00',
                selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-description').alltext_normalized)


class TestStudentItemValue(test.TestCase):
    def test_custom_cssclass(self):
        testperiod = baker.make('core.Period')
        selector = htmls.S(devilry_listbuilder.period.StudentItemValue(value=testperiod).render())
        self.assertTrue(selector.exists('.devilry-cradmin-perioditemvalue-student'))

    def test_title(self):
        testperiod = baker.make('core.Period',
                                parentnode__long_name='Test Subject',
                                long_name='Test Period')
        selector = htmls.S(devilry_listbuilder.period.StudentItemValue(value=testperiod).render())
        self.assertEqual(
                'Test Subject - Test Period',
                selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_description_no_assignments(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        testperiod_annotated = Period.objects\
            .extra_annotate_with_assignmentcount_for_studentuser(user=testuser)\
            .get(id=testperiod.id)
        selector = htmls.S(devilry_listbuilder.period.StudentItemValue(value=testperiod_annotated).render())
        self.assertEqual(
                '0 assignments',
                selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-description').alltext_normalized)

    def test_description_single_assignment(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent', user=testuser, period=testperiod)
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        baker.make('core.Candidate',
                   assignment_group__parentnode=testassignment,
                   relatedstudent=relatedstudent)
        testperiod_annotated = Period.objects\
            .extra_annotate_with_assignmentcount_for_studentuser(user=testuser)\
            .get(id=testperiod.id)
        selector = htmls.S(devilry_listbuilder.period.StudentItemValue(value=testperiod_annotated).render())
        self.assertEqual(
                '1 assignment',
                selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-description').alltext_normalized)

    def test_description_multiple_assignments_assignment(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent', user=testuser, period=testperiod)
        testassignment1 = baker.make('core.Assignment', parentnode=testperiod)
        baker.make('core.Candidate',
                   assignment_group__parentnode=testassignment1,
                   relatedstudent=relatedstudent)
        testassignment2 = baker.make('core.Assignment', parentnode=testperiod)
        baker.make('core.Candidate',
                   assignment_group__parentnode=testassignment2,
                   relatedstudent=relatedstudent)
        testperiod_annotated = Period.objects\
            .extra_annotate_with_assignmentcount_for_studentuser(user=testuser)\
            .get(id=testperiod.id)
        selector = htmls.S(devilry_listbuilder.period.StudentItemValue(value=testperiod_annotated).render())
        self.assertEqual(
                '2 assignments',
                selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-description').alltext_normalized)

    def test_no_qualified_for_final_exam_status(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        testperiod_annotated = Period.objects\
            .extra_annotate_with_user_qualifies_for_final_exam(user=testuser)\
            .get(id=testperiod.id)
        selector = htmls.S(devilry_listbuilder.period.StudentItemValue(value=testperiod_annotated).render())
        self.assertFalse(selector.exists('.devilry-cradmin-perioditemvalue-student-qualifedforexam'))

    def test_qualified_for_final_exam(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=testuser)
        status = baker.make('devilry_qualifiesforexam.Status', period=testperiod,
                            status=Status.READY)
        baker.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=relatedstudent,
                   status=status,
                   qualifies=True)
        testperiod_annotated = Period.objects\
            .extra_annotate_with_user_qualifies_for_final_exam(user=testuser)\
            .get(id=testperiod.id)
        selector = htmls.S(devilry_listbuilder.period.StudentItemValue(value=testperiod_annotated).render())
        self.assertTrue(selector.exists('.devilry-cradmin-perioditemvalue-student-qualifedforexam-yes'))
        self.assertFalse(selector.exists('.devilry-cradmin-perioditemvalue-student-qualifedforexam-no'))
        self.assertEqual(
                'Qualified for final exam',
                selector.one('.devilry-cradmin-perioditemvalue-student-qualifedforexam').alltext_normalized)

    def test_not_qualified_for_final_exam(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=testuser)
        status = baker.make('devilry_qualifiesforexam.Status', period=testperiod,
                            status=Status.READY)
        baker.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=relatedstudent,
                   status=status,
                   qualifies=False)
        testperiod_annotated = Period.objects\
            .extra_annotate_with_user_qualifies_for_final_exam(user=testuser)\
            .get(id=testperiod.id)
        selector = htmls.S(devilry_listbuilder.period.StudentItemValue(value=testperiod_annotated).render())
        self.assertFalse(selector.exists('.devilry-cradmin-perioditemvalue-student-qualifedforexam-yes'))
        self.assertTrue(selector.exists('.devilry-cradmin-perioditemvalue-student-qualifedforexam-no'))
        self.assertEqual(
                'NOT qualified for final exam',
                selector.one('.devilry-cradmin-perioditemvalue-student-qualifedforexam').alltext_normalized)
