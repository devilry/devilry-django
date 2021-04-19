# -*- coding: utf-8 -*-


# 3rd party imports
from model_bakery import baker

# Django imports
from django import test

# CrAdmin imports
from cradmin_legacy import cradmin_testhelpers

# Devilry imports
from devilry.project.common import settings
from devilry.devilry_qualifiesforexam.views import qualification_preview_view
from devilry.devilry_qualifiesforexam import models as status_models


class TestQualificationPreviewView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = qualification_preview_view.QualificationPreviewView

    def test_get(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        mockresponse = self.mock_getrequest(
                cradmin_role=testperiod,
                sessionmock={
                    'passing_relatedstudentids': [],
                    'plugintypeid': 'some_plugintypeid'
                })
        self.assertEqual(mockresponse.response.status_code, 200)

    def test_get_back_button(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                sessionmock={
                    'passing_relatedstudentids': [],
                    'plugintypeid': 'some_plugintypeid'
                })
        self.assertTrue(mockresponse.selector.one('#devilry_qualifiesforexam_back_index_button'))

    def test_get_back_button_text(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                sessionmock={
                    'passing_relatedstudentids': [],
                    'plugintypeid': 'some_plugintypeid'
                })
        self.assertEqual(
                mockresponse.selector.one('#devilry_qualifiesforexam_back_index_button').alltext_normalized,
                'Back')

    def test_get_save_button(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                sessionmock={
                    'passing_relatedstudentids': [],
                    'plugintypeid': 'some_plugintypeid'
                })
        self.assertTrue(mockresponse.selector.one('#devilry_qualifiesforexam_save_button'))

    def test_get_save_button_text(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                sessionmock={
                    'passing_relatedstudentids': [],
                    'plugintypeid': 'some_plugintypeid'
                })
        self.assertEqual(
                mockresponse.selector.one('#devilry_qualifiesforexam_save_button').alltext_normalized,
                'Save')

    def test_redirect_to_status_view_if_status_ready_exists_for_period(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        baker.make('devilry_qualifiesforexam.Status',
                   period=testperiod,
                   status=status_models.Status.READY,
                   plugin='someplugin')
        mockresponse = self.mock_getrequest(cradmin_role=testperiod)
        self.assertEqual(mockresponse.response.status_code, 302)

    def test_post_save_302(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        relatedstudents = baker.make('core.RelatedStudent', period=testperiod, _quantity=20)
        passing_studentids = [student.id for student in relatedstudents]

        mockresponse = self.mock_http302_postrequest(
            cradmin_role=testperiod,
            sessionmock={
                'passing_relatedstudentids': passing_studentids,
                'plugintypeid': 'someplugin_id'
            },
            requestkwargs={
                'data': {
                    'save': 'unused value',
                }
            })
        self.assertEqual(mockresponse.response.status_code, 302)

    def test_post_save_session_is_deleted(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        relatedstudents = baker.make('core.RelatedStudent', period=testperiod, _quantity=20)
        passing_studentids = [student.id for student in relatedstudents]

        mockresponse = self.mock_http302_postrequest(
            cradmin_role=testperiod,
            sessionmock={
                'passing_relatedstudentids': passing_studentids,
                'plugintypeid': 'someplugin_id'
            },
            requestkwargs={
                'data': {
                    'save': 'unused value',
                }
            })
        self.assertEqual(len(mockresponse.request.session), 0)

    def test_post_back_302(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        mockresponse = self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestkwargs={
                'data': {
                    'back': 'unused value',
                }
            })
        self.assertEqual(mockresponse.response.status_code, 302)

    def test_post_back_session_is_deleted(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        relatedstudents = baker.make('core.RelatedStudent', period=testperiod, _quantity=20)
        passing_studentids = [student.id for student in relatedstudents]

        mockresponse = self.mock_http302_postrequest(
            cradmin_role=testperiod,
            sessionmock={
                'passing_relatedstudentids': passing_studentids,
                'plugintypeid': 'someplugin_id'
            },
            requestkwargs={
                'data': {
                    'back': 'unused value',
                }
            })
        self.assertEqual(len(mockresponse.request.session), 0)

    def test_post_save_status(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        admin_user = baker.make(settings.AUTH_USER_MODEL)
        relatedstudents = baker.make('core.RelatedStudent', period=testperiod, _quantity=20)
        passing_studentids = [student.id for student in relatedstudents]

        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            requestuser=admin_user,
            sessionmock={
                'passing_relatedstudentids': passing_studentids,
                'plugintypeid': 'someplugin_id'
            },
            requestkwargs={
                'data': {
                    'save': 'unused value',
                }
            })

        statuses = status_models.Status.objects.filter(period=testperiod)
        self.assertEqual(len(statuses), 1)
        status = statuses[0]
        self.assertEqual(status.user, admin_user)
        self.assertEqual(status.status, status_models.Status.READY)

    def test_post_save_all_students_qualify(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        relatedstudents = baker.make('core.RelatedStudent', period=testperiod, _quantity=20)
        passing_studentids = [student.id for student in relatedstudents]

        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            sessionmock={
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
        self.assertEqual(len(qualification_entries), 20)
        for qualification_entry in qualification_entries:
            self.assertTrue(qualification_entry.qualifies)

    def test_post_save_no_students_qualify(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        baker.make('core.RelatedStudent', period=testperiod, _quantity=20)
        passing_studentids = []

        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            sessionmock={
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
        self.assertEqual(len(qualification_entries), 20)
        for qualification_entry in qualification_entries:
            self.assertFalse(qualification_entry.qualifies)

    def test_post_subset_of_students_qualify(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        relatedstudents = baker.make('core.RelatedStudent', period=testperiod, _quantity=20)

        # RelatedStudents with id 1-10 qualify, the rest do not
        passing_studentids = [student.id for student in relatedstudents[:10]]

        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            sessionmock={
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

        self.assertEqual(len(qualifying_students), 10)
        self.assertEqual(len(non_qualifying_students), 10)

        for student_entry in qualifying_students:
            self.assertIn(student_entry.relatedstudent.id, passing_studentids)

        for student_entry in non_qualifying_students:
            self.assertNotIn(student_entry.relatedstudent.id, passing_studentids)

    def test_num_queries(self):
        testperiod = baker.make('core.Period')
        baker.make('core.RelatedStudent', period=testperiod, _quantity=100)
        with self.assertNumQueries(3):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                sessionmock={
                    'passing_relatedstudentids': [],
                    'plugintypeid': 'some_plugintypeid'
                }
            )


class TestQualificationPreviewViewTableRendering(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = qualification_preview_view.QualificationPreviewView

    def test_table_is_rendered(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        baker.make('core.RelatedStudent', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            sessionmock={
                'passing_relatedstudentids': [],
                'plugintypeid': 'someplugin_id'
            })
        self.assertTrue(mockresponse.selector.exists('.devilry-qualifiesforexam-table'))

    def test_table_row_is_rendered(self):
        # Tests that two rows are rendered, on for the header and one for the student
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        baker.make('core.RelatedStudent', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            sessionmock={
                'passing_relatedstudentids': [],
                'plugintypeid': 'someplugin_id'
            })
        self.assertEqual(len(mockresponse.selector.list('.devilry-qualifiesforexam-tr')), 2)

    def test_table_row_is_rendered_multiple_students(self):
        # Tests that 21 rows are rendered, one for the table header and twenty(one for each student)
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        baker.make('core.RelatedStudent', period=testperiod, _quantity=20)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            sessionmock={
                'passing_relatedstudentids': [],
                'plugintypeid': 'someplugin_id'
            })
        self.assertEqual(len(mockresponse.selector.list('.devilry-qualifiesforexam-tr')), 21)

    def test_table_data_studentinfo_is_rendered(self):
        # Tests that a td element of class 'devilry-qualifiesforexam-cell-studentinfo' is rendered.
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        baker.make('core.RelatedStudent', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            sessionmock={
                'passing_relatedstudentids': [],
                'plugintypeid': 'someplugin_id'
            })
        self.assertEqual(len(mockresponse.selector.list('.devilry-qualifiesforexam-cell-studentinfo')), 1)

    def test_table_data_qualify_result_is_rendered(self):
        # Tests that a td element of class 'devilry-qualifiesforexam-cell-qualify' is rendered.
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        baker.make('core.RelatedStudent', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            sessionmock={
                'passing_relatedstudentids': [],
                'plugintypeid': 'someplugin_id'
            })
        self.assertEqual(len(mockresponse.selector.list('.devilry-qualifiesforexam-cell-qualify')), 1)

    def test_table_header_cell_data(self):
        # Test a more complete example of data contained in cells for two students, one qualifying and one not.
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        baker.make('core.RelatedStudent', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            sessionmock={
                'passing_relatedstudentids': [],
                'plugintypeid': 'someplugin_id'
            })
        table_headers = mockresponse.selector.list('.devilry-qualifiesforexam-th')
        self.assertEqual(table_headers[0].alltext_normalized, 'Student')
        self.assertEqual(table_headers[1].alltext_normalized, 'Qualified for final exams')

    def test_table_student_row_data_student_does_not_qualify(self):
        # Test a more complete example of data contained in cells for two students, one qualifying and one not.
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        relatedstudent = baker.make('core.RelatedStudent',
                                    period=testperiod,
                                    user=baker.make(settings.AUTH_USER_MODEL,
                                                    fullname='Jane Doe',
                                                    shortname='janedoe'))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            sessionmock={
                'passing_relatedstudentids': [],
                'plugintypeid': 'someplugin_id'
            })
        studentinfo = mockresponse.selector.one('.devilry-qualifiesforexam-cell-studentinfo')
        self.assertEqual(studentinfo.alltext_normalized, '{} {}'.format(relatedstudent.user.fullname,
                                                                         relatedstudent.user.shortname))
        self.assertEqual(mockresponse.selector.one('.devilry-qualifiesforexam-cell-qualify').alltext_normalized, 'NO')

    def test_table_student_row_data_student_qualifies(self):
        # Test a more complete example of data contained in cells for two students, one qualifying and one not.
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        relatedstudent = baker.make('core.RelatedStudent',
                                    period=testperiod,
                                    user=baker.make(settings.AUTH_USER_MODEL,
                                                    fullname='Jane Doe',
                                                    shortname='janedoe'))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            sessionmock={
                'passing_relatedstudentids': [relatedstudent.id],
                'plugintypeid': 'someplugin_id'
            })
        studentinfo = mockresponse.selector.one('.devilry-qualifiesforexam-cell-studentinfo')
        self.assertEqual(studentinfo.alltext_normalized, '{} {}'.format(relatedstudent.user.fullname,
                                                                         relatedstudent.user.shortname))
        self.assertEqual(mockresponse.selector.one('.devilry-qualifiesforexam-cell-qualify').alltext_normalized, 'YES')
