# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# 3rd party imports
from model_mommy import mommy

# Django imports
from django import test

# CrAdmin imports
from django_cradmin import cradmin_testhelpers

# Devilry imports
from devilry.project.common import settings
from devilry.devilry_qualifiesforexam.views import qualification_preview_view
from devilry.devilry_qualifiesforexam import models as status_models


class TestQualificationPreviewView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = qualification_preview_view.QualificationPreviewView

    def test_get(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        admin_user = mommy.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_getrequest(
                requestuser=admin_user,
                cradmin_role=testperiod,
                sessionmock={
                    'qualifying_assignmentids': [],
                    'passing_relatedstudentids': [],
                    'plugintypeid': 'someplugin_id'
                })
        self.assertEquals(mockresponse.response.status_code, 200)

    def test_redirect_to_export_view_if_status_ready_exists_for_period(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        admin_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_qualifiesforexam.Status',
                   period=testperiod,
                   status=status_models.Status.READY,
                   plugin='someplugin')
        mockresponse = self.mock_getrequest(cradmin_role=testperiod, requestuser=admin_user)
        self.assertEquals(mockresponse.response.status_code, 302)

    def test_post_save_302(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        admin_user = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudents = mommy.make('core.RelatedStudent', period=testperiod, _quantity=20)
        passing_studentids = [student.id for student in relatedstudents]

        mockresponse = self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestuser=admin_user,
            sessionmock={
                'qualifying_assignmentids': [],
                'passing_relatedstudentids': passing_studentids,
                'plugintypeid': 'someplugin_id'
            },
            requestkwargs={
                'data': {
                    'save': 'unused value',
                }
            })

        self.assertEquals(mockresponse.response.status_code, 302)

    def test_post_back_302(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        admin_user = mommy.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestuser=admin_user,
            requestkwargs={
                'data': {
                    'back': 'unused value',
                }
            })
        self.assertEquals(mockresponse.response.status_code, 302)

    def test_post_save_status(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        admin_user = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudents = mommy.make('core.RelatedStudent', period=testperiod, _quantity=20)
        passing_studentids = [student.id for student in relatedstudents]

        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestuser=admin_user,
            sessionmock={
                'qualifying_assignmentids': [],
                'passing_relatedstudentids': passing_studentids,
                'plugintypeid': 'someplugin_id'
            },
            requestkwargs={
                'data': {
                    'save': 'unused value',
                }
            })

        statuses = status_models.Status.objects.filter(period=testperiod)
        self.assertEquals(len(statuses), 1)
        status = statuses[0]
        self.assertEquals(status.user, admin_user)
        self.assertEquals(status.status, status_models.Status.READY)

    def test_post_save_all_students_qualify(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        admin_user = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudents = mommy.make('core.RelatedStudent', period=testperiod, _quantity=20)
        passing_studentids = [student.id for student in relatedstudents]

        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestuser=admin_user,
            sessionmock={
                'qualifying_assignmentids': [],
                'passing_relatedstudentids': passing_studentids,
                'plugintypeid': 'someplugin_id'
            },
            requestkwargs={
                'data': {
                    'save': 'unused value',
                }
            })

        status = status_models.Status.objects.get(period=testperiod)
        qualification_entries = status_models.QualifiesForFinalExam.objects.filter(status=status)
        self.assertEquals(len(qualification_entries), 20)
        for qualification_entry in qualification_entries:
            self.assertTrue(qualification_entry.qualifies)

    def test_post_save_no_students_qualify(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        admin_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.RelatedStudent', period=testperiod, _quantity=20)
        passing_studentids = []

        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestuser=admin_user,
            sessionmock={
                'qualifying_assignmentids': [],
                'passing_relatedstudentids': passing_studentids,
                'plugintypeid': 'someplugin_id'
            },
            requestkwargs={
                'data': {
                    'save': 'unused value',
                }
            })

        status = status_models.Status.objects.get(period=testperiod)
        qualification_entries = status_models.QualifiesForFinalExam.objects.filter(status=status)
        self.assertEquals(len(qualification_entries), 20)
        for qualification_entry in qualification_entries:
            self.assertFalse(qualification_entry.qualifies)

    def test_post_subset_of_students_qualify(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        admin_user = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudents = mommy.make('core.RelatedStudent', period=testperiod, _quantity=20)

        # RelatedStudents with id 1-10 qualify, the rest do not
        passing_studentids = [student.id for student in relatedstudents[:10]]

        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestuser=admin_user,
            sessionmock={
                'qualifying_assignmentids': [],
                'passing_relatedstudentids': passing_studentids,
                'plugintypeid': 'someplugin_id'
            },
            requestkwargs={
                'data': {
                    'save': 'unused value',
                }
            })

        status = status_models.Status.objects.get(period=testperiod)
        qualifying_students = status_models.QualifiesForFinalExam.objects.filter(status=status, qualifies=True)
        non_qualifying_students = status_models.QualifiesForFinalExam.objects.filter(status=status, qualifies=False)

        self.assertEquals(len(qualifying_students), 10)
        self.assertEquals(len(non_qualifying_students), 10)

        for student_entry in qualifying_students:
            self.assertIn(student_entry.relatedstudent.id, passing_studentids)

        for student_entry in non_qualifying_students:
            self.assertNotIn(student_entry.relatedstudent.id, passing_studentids)