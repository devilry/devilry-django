import unittest
from datetime import datetime
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from model_bakery import baker

from devilry.apps.core.models import Period, Subject
from devilry.apps.core.models.model_utils import EtagMismatchException
from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_qualifiesforexam.models import Status


class TestPeriodQuerySetFilterActive(TestCase):
    def test_filter_active(self):
        baker.make_recipe('devilry.apps.core.period_old')
        active_period = baker.make_recipe('devilry.apps.core.period_active')
        baker.make_recipe('devilry.apps.core.period_future')
        self.assertEqual(
                set(Period.objects.filter_active()),
                {active_period})


class TestPeriodQuerySetFilterHasStarted(TestCase):
    def test_filter_active(self):
        old_period = baker.make_recipe('devilry.apps.core.period_old')
        active_period = baker.make_recipe('devilry.apps.core.period_active')
        baker.make_recipe('devilry.apps.core.period_future')
        self.assertEqual(
                set(Period.objects.filter_has_started()),
                {old_period, active_period})


class TestPeriodQuerySetExtraAnnotateWithAssignmentcountForStudentuser(TestCase):
    def test_no_assignments(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        annotated_period = Period.objects\
            .extra_annotate_with_assignmentcount_for_studentuser(user=testuser)\
            .get(id=testperiod.id)
        self.assertEqual(0, annotated_period.assignmentcount_for_studentuser)

    def test_no__assignments_where_candidate(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        baker.make('core.Candidate',  # Not testuser Candidate
                   assignment_group__parentnode=testassignment,
                   relatedstudent__period=testperiod)
        annotated_period = Period.objects\
            .extra_annotate_with_assignmentcount_for_studentuser(user=testuser)\
            .get(id=testperiod.id)
        self.assertEqual(0, annotated_period.assignmentcount_for_studentuser)

    def test_single_assignment(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        testassignment = baker.make('core.Assignment', parentnode=testperiod)
        baker.make('core.Candidate',
                   assignment_group__parentnode=testassignment,
                   relatedstudent__user=testuser,
                   relatedstudent__period=testperiod)
        annotated_period = Period.objects\
            .extra_annotate_with_assignmentcount_for_studentuser(user=testuser)\
            .get(id=testperiod.id)
        self.assertEqual(1, annotated_period.assignmentcount_for_studentuser)

    def test_multiple_assignments(self):
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
        testassignment3 = baker.make('core.Assignment', parentnode=testperiod)
        baker.make('core.Candidate',
                   assignment_group__parentnode=testassignment3,
                   relatedstudent=relatedstudent)
        annotated_period = Period.objects\
            .extra_annotate_with_assignmentcount_for_studentuser(user=testuser)\
            .get(id=testperiod.id)
        self.assertEqual(3, annotated_period.assignmentcount_for_studentuser)

    def test_multiple_periods(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod1 = baker.make('core.Period')
        relatedstudent1 = baker.make('core.RelatedStudent', user=testuser, period=testperiod1)
        testassignment1 = baker.make('core.Assignment', parentnode=testperiod1)
        baker.make('core.Candidate',
                   assignment_group__parentnode=testassignment1,
                   relatedstudent=relatedstudent1)
        testperiod2 = baker.make('core.Period')
        baker.make('core.RelatedStudent', user=testuser, period=testperiod2)
        annotated_period1 = Period.objects\
            .extra_annotate_with_assignmentcount_for_studentuser(user=testuser)\
            .get(id=testperiod1.id)
        annotated_period2 = Period.objects\
            .extra_annotate_with_assignmentcount_for_studentuser(user=testuser)\
            .get(id=testperiod2.id)
        self.assertEqual(1, annotated_period1.assignmentcount_for_studentuser)
        self.assertEqual(0, annotated_period2.assignmentcount_for_studentuser)


class TestPeriodQuerySetExtraAnnotateWithUserQualifiesForFinalExam(TestCase):
    def test_not_set(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        baker.make('devilry_qualifiesforexam.Status', period=testperiod,
                   status=Status.READY)
        annotated_period = Period.objects\
            .extra_annotate_with_user_qualifies_for_final_exam(user=testuser)\
            .get(id=testperiod.id)
        self.assertIsNone(annotated_period.user_qualifies_for_final_exam)

    def test_no_status(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        annotated_period = Period.objects\
            .extra_annotate_with_user_qualifies_for_final_exam(user=testuser)\
            .get(id=testperiod.id)
        self.assertIsNone(annotated_period.user_qualifies_for_final_exam)

    def test_not_ready_qualified(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=testuser)
        status = baker.make('devilry_qualifiesforexam.Status', period=testperiod,
                            status=Status.NOTREADY)
        baker.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=relatedstudent,
                   status=status,
                   qualifies=True)
        annotated_period = Period.objects\
            .extra_annotate_with_user_qualifies_for_final_exam(user=testuser)\
            .get(id=testperiod.id)
        self.assertIsNone(annotated_period.user_qualifies_for_final_exam)

    def test_not_ready_not_qualified(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=testuser)
        status = baker.make('devilry_qualifiesforexam.Status', period=testperiod,
                            status=Status.NOTREADY)
        baker.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=relatedstudent,
                   status=status,
                   qualifies=False)
        annotated_period = Period.objects\
            .extra_annotate_with_user_qualifies_for_final_exam(user=testuser)\
            .get(id=testperiod.id)
        self.assertIsNone(annotated_period.user_qualifies_for_final_exam)

    def test_not_ready_qualifies_none(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=testuser)
        status = baker.make('devilry_qualifiesforexam.Status', period=testperiod,
                            status=Status.NOTREADY)
        baker.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=relatedstudent,
                   status=status,
                   qualifies=None)
        annotated_period = Period.objects\
            .extra_annotate_with_user_qualifies_for_final_exam(user=testuser)\
            .get(id=testperiod.id)
        self.assertIsNone(annotated_period.user_qualifies_for_final_exam)

    def test_ready_qualified(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=testuser)
        status = baker.make('devilry_qualifiesforexam.Status', period=testperiod,
                            status=Status.READY)
        baker.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=relatedstudent,
                   status=status,
                   qualifies=True)
        annotated_period = Period.objects\
            .extra_annotate_with_user_qualifies_for_final_exam(user=testuser)\
            .get(id=testperiod.id)
        self.assertTrue(annotated_period.user_qualifies_for_final_exam)

    def test_ready_not_qualified(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=testuser)
        status = baker.make('devilry_qualifiesforexam.Status', period=testperiod,
                            status=Status.READY)
        baker.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=relatedstudent,
                   status=status,
                   qualifies=False)
        annotated_period = Period.objects\
            .extra_annotate_with_user_qualifies_for_final_exam(user=testuser)\
            .get(id=testperiod.id)
        self.assertFalse(annotated_period.user_qualifies_for_final_exam)

    def test_ready_qualifies_none(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=testuser)
        status = baker.make('devilry_qualifiesforexam.Status', period=testperiod,
                            status=Status.READY)
        baker.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=relatedstudent,
                   status=status,
                   qualifies=None)
        annotated_period = Period.objects\
            .extra_annotate_with_user_qualifies_for_final_exam(user=testuser)\
            .get(id=testperiod.id)
        self.assertIsNone(annotated_period.user_qualifies_for_final_exam)

    def test_almostready_qualified(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=testuser)
        status = baker.make('devilry_qualifiesforexam.Status', period=testperiod,
                            status=Status.ALMOSTREADY)
        baker.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=relatedstudent,
                   status=status,
                   qualifies=True)
        annotated_period = Period.objects\
            .extra_annotate_with_user_qualifies_for_final_exam(user=testuser)\
            .get(id=testperiod.id)
        self.assertTrue(annotated_period.user_qualifies_for_final_exam)

    def test_almostready_not_qualified(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=testuser)
        status = baker.make('devilry_qualifiesforexam.Status', period=testperiod,
                            status=Status.ALMOSTREADY)
        baker.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=relatedstudent,
                   status=status,
                   qualifies=False)
        annotated_period = Period.objects\
            .extra_annotate_with_user_qualifies_for_final_exam(user=testuser)\
            .get(id=testperiod.id)
        self.assertFalse(annotated_period.user_qualifies_for_final_exam)

    def test_almostready_qualifies_none(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=testuser)
        status = baker.make('devilry_qualifiesforexam.Status', period=testperiod,
                            status=Status.ALMOSTREADY)
        baker.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=relatedstudent,
                   status=status,
                   qualifies=None)
        annotated_period = Period.objects\
            .extra_annotate_with_user_qualifies_for_final_exam(user=testuser)\
            .get(id=testperiod.id)
        self.assertIsNone(annotated_period.user_qualifies_for_final_exam)

    def test_multiple_statuses_use_last(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=testuser)
        oldstatus = baker.make('devilry_qualifiesforexam.Status', period=testperiod,
                               status=Status.READY,
                               createtime=timezone.now() - timedelta(days=2))
        baker.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=relatedstudent,
                   status=oldstatus,
                   qualifies=True)
        baker.make('devilry_qualifiesforexam.Status', period=testperiod,  # The last status
                   status=Status.NOTREADY,
                   createtime=timezone.now())
        annotated_period = Period.objects\
            .extra_annotate_with_user_qualifies_for_final_exam(user=testuser)\
            .get(id=testperiod.id)
        self.assertIsNone(annotated_period.user_qualifies_for_final_exam)

    def test_use_correct_period(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        otherperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent', period=otherperiod, user=testuser)
        status = baker.make('devilry_qualifiesforexam.Status', period=otherperiod,
                            status=Status.READY)
        baker.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=relatedstudent,
                   status=status,
                   qualifies=True)
        testperiod = baker.make('core.Period')
        annotated_period = Period.objects\
            .extra_annotate_with_user_qualifies_for_final_exam(user=testuser)\
            .get(id=testperiod.id)
        self.assertIsNone(annotated_period.user_qualifies_for_final_exam)


class TestPeriodQuerySetPermission(TestCase):
    def test_filter_user_is_admin_is_not_admin_on_anything(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Period')
        self.assertFalse(Period.objects.filter_user_is_admin(user=testuser).exists())

    def test_filter_user_is_admin_superuser(self):
        testuser = baker.make(settings.AUTH_USER_MODEL, is_superuser=True)
        testperiod = baker.make('core.Period')
        self.assertEqual(
            {testperiod},
            set(Period.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_ignore_periods_where_not_in_group(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        baker.make('core.Period')
        periodpermissiongroup = baker.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        self.assertEqual(
                {testperiod},
                set(Period.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make('core.Period')
        periodpermissiongroup = baker.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser, permissiongroup=periodpermissiongroup.permissiongroup)
        self.assertEqual(
                {testperiod},
                set(Period.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_on_subject(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testsubject = baker.make('core.Subject')
        testperiod = baker.make('core.Period', parentnode=testsubject)
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            subject=testsubject)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=subjectpermissiongroup.permissiongroup)
        self.assertEqual(
                {testperiod},
                set(Period.objects.filter_user_is_admin(user=testuser)))

    def test_filter_user_is_admin_distinct(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testsubject = baker.make('core.Subject')
        testperiod = baker.make('core.Period', parentnode=testsubject)
        subjectpermissiongroup1 = baker.make('devilry_account.SubjectPermissionGroup',
                                             subject=testsubject)
        subjectpermissiongroup2 = baker.make('devilry_account.SubjectPermissionGroup',
                                             subject=testsubject)
        periodpermissiongroup1 = baker.make('devilry_account.PeriodPermissionGroup',
                                            period=testperiod)
        periodpermissiongroup2 = baker.make('devilry_account.PeriodPermissionGroup',
                                            period=testperiod)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=subjectpermissiongroup1.permissiongroup)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=subjectpermissiongroup2.permissiongroup)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=periodpermissiongroup1.permissiongroup)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testuser,
                   permissiongroup=periodpermissiongroup2.permissiongroup)
        self.assertEqual(
                {testperiod},
                set(Period.objects.filter_user_is_admin(user=testuser)))

@unittest.skip('Tests marked as OLD, should they be deleted?')
class TestPeriodOld(TestCase, TestHelper):
    """
    Do not add new tests to this testcase, add to the newer testcases above,
    or add new testcases and use corebuilder instead.
    """

    def setUp(self):
        self.add(nodes="uio:admin(uioadmin).ifi",
                 subjects=["inf1100"],
                 periods=["old:begins(-2):ends(1)", "looong:begins(-1):ends(10)"],
                 assignments=["assignment1", "assignment2"],
                 assignmentgroups=["g1:examiner(examiner1)", "g2:examiner(examiner2)"])

    def test_unique(self):
        n = Period(parentnode=Subject.objects.get(short_name='inf1100'),
                   short_name='old', long_name='Old',
                   start_time=timezone.now(),
                   end_time=timezone.now())
        self.assertRaises(IntegrityError, n.save)

    def test_etag_update(self):
        etag = timezone.now()
        obj = self.inf1100_looong
        obj.long_name = 'Updated'
        self.assertRaises(EtagMismatchException, obj.etag_update, etag)
        try:
            obj.etag_update(etag)
        except EtagMismatchException as e:
            # Should not raise exception
            obj.etag_update(e.etag)
        obj2 = Period.objects.get(id=obj.id)
        self.assertEqual(obj2.long_name, 'Updated')

    def test_clean(self):
        self.inf1100_looong.start_time = datetime(2010, 1, 1)
        self.inf1100_looong.end_time = datetime(2011, 1, 1)
        self.inf1100_looong.clean()
        self.inf1100_looong.start_time = datetime(2012, 1, 1)
        self.assertRaises(ValidationError, self.inf1100_looong.clean)

    def test_where_is_examiner(self):
        q = Period.where_is_examiner(self.examiner1).order_by('short_name')
        self.assertEqual(q.count(), 2)
        self.assertEqual(q[0].short_name, 'looong')
        self.assertEqual(q[1].short_name, 'old')
        # Add on different period
        self.add_to_path('uio.ifi;inf1010.spring10.oblig1.student1:examiner(examiner1)')
        self.assertEqual(q.count(), 3)
        self.assertEqual(q[0].short_name, 'looong')
        self.assertEqual(q[1].short_name, 'old')
        self.assertEqual(q[2].short_name, 'spring10')

    def test_published_where_is_examiner(self):
        examiner1 = get_user_model().objects.get(shortname='examiner1')
        self.add_to_path('uio.ifi;inf1010.spring10:begins(-1):ends(2).oblig1.student1:examiner(examiner1)')
        q = Period.published_where_is_examiner(examiner1).order_by('short_name')
        self.assertEqual(q.count(), 3)
        assignment1010 = self.inf1010_spring10_oblig1_student1.parentnode
        assignment1010.publishing_time = timezone.now() + timedelta(10)
        assignment1010.save()
        self.assertEqual(q.count(), 2)

    def test_is_empty(self):
        self.assertFalse(self.inf1100_old.is_empty())
        self.add(nodes="uio.ifi", subjects=['duck9000'], periods=['emptyperiod'])
        self.assertTrue(self.duck9000_emptyperiod.is_empty())

    def test_q_is_active(self):
        activeperiods = Period.objects.filter(Period.q_is_active())
        self.assertEqual(activeperiods.count(), 1)
        self.assertEqual(activeperiods[0], self.inf1100_looong)
        self.inf1100_old.end_time = timezone.now() + timedelta(days=10)
        self.inf1100_old.save()
        self.assertEqual(Period.objects.filter(Period.q_is_active()).count(), 2)
