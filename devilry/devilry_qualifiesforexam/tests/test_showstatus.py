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


class TestQualificationStatusView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = qualification_preview_view.QualificationStatusView

    def test_get(self):
        testperiod = mommy.make('core.Period')
        teststatus = mommy.make('devilry_qualifiesforexam.Status', period=testperiod)
        mockresponse = self.mock_getrequest(
                cradmin_role=testperiod,
                viewkwargs={
                    'statusid': teststatus.id
                })
        self.assertEquals(mockresponse.response.status_code, 200)

    def test_get_retracted_message(self):
        testperiod = mommy.make('core.Period')
        teststatus = mommy.make('devilry_qualifiesforexam.Status',
                                period=testperiod,
                                status=status_models.Status.NOTREADY,
                                message='retracted')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                viewkwargs={
                    'statusid': teststatus.id
                })
        retracted_message_element = mockresponse.selector.one('#devilry_qualifiesforexam_retracted_message')
        self.assertTrue(retracted_message_element)
        self.assertEquals(retracted_message_element.alltext_normalized, 'retracted')

    def test_get_back_button(self):
        testperiod = mommy.make('core.Period')
        teststatus = mommy.make('devilry_qualifiesforexam.Status', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                viewkwargs={
                    'statusid': teststatus.id
                })
        self.assertTrue(mockresponse.selector.one('#devilry_qualifiesforexam_back_index_button'))

    def test_get_retract_button_link(self):
        testperiod = mommy.make('core.Period')
        teststatus = mommy.make('devilry_qualifiesforexam.Status', period=testperiod, status=status_models.Status.READY)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                viewkwargs={
                    'statusid': teststatus.id
                })
        self.assertTrue(mockresponse.selector.one('#devilry_qualifiesforexam_retract_link'))

    def test_no_retract_button_when_status_is_not_ready(self):
        testperiod = mommy.make('core.Period')
        teststatus = mommy.make('devilry_qualifiesforexam.Status', period=testperiod,
                                status=status_models.Status.NOTREADY)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                viewkwargs={
                    'statusid': teststatus.id
                })
        self.assertFalse(mockresponse.selector.exists('#devilry_qualifiesforexam_retract_link'))

    def test_get_print_button_link(self):
        testperiod = mommy.make('core.Period')
        teststatus = mommy.make('devilry_qualifiesforexam.Status', period=testperiod, status=status_models.Status.READY)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                viewkwargs={
                    'statusid': teststatus.id
                })
        self.assertTrue(mockresponse.selector.one('#devilry_qualifiesforexam_print_link'))

    def test_no_print_button_when_status_is_not_ready(self):
        testperiod = mommy.make('core.Period')
        teststatus = mommy.make('devilry_qualifiesforexam.Status', period=testperiod,
                                status=status_models.Status.NOTREADY)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                viewkwargs={
                    'statusid': teststatus.id
                })
        self.assertFalse(mockresponse.selector.exists('#devilry_qualifiesforexam_print_link'))

    def test_num_queries(self):
        testperiod = mommy.make('core.Period')
        admin_user = mommy.make(settings.AUTH_USER_MODEL)
        teststatus = mommy.make('devilry_qualifiesforexam.Status',
                                period=testperiod,
                                status=status_models.Status.READY,
                                user=admin_user,
                                plugin='someplugin')
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   status=teststatus,
                   qualifies=True,
                   _quantity=10)
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   status=teststatus,
                   qualifies=False,
                   _quantity=10)
        with self.assertNumQueries(4):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                requestuser=admin_user,
                viewkwargs={
                    'statusid': teststatus.id
                },
            )


class TestQualificationStatusPreviewTableRendering(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = qualification_preview_view.QualificationStatusView

    def test_table_is_rendered(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent', period=testperiod)
        teststatus = mommy.make('devilry_qualifiesforexam.Status', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'statusid': teststatus.id
            },
            sessionmock={
                'qualifying_assignmentids': [],
                'passing_relatedstudentids': [],
                'plugintypeid': 'someplugin_id'
            })
        self.assertTrue(mockresponse.selector.exists('.devilry-qualifiesforexam-table'))

    def test_table_row_is_rendered(self):
        # Tests that two rows are rendered, on for the header and one for the student
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent', period=testperiod)
        teststatus = mommy.make('devilry_qualifiesforexam.Status', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'statusid': teststatus.id
            },
            sessionmock={
                'qualifying_assignmentids': [],
                'passing_relatedstudentids': [],
                'plugintypeid': 'someplugin_id'
            })
        self.assertEquals(len(mockresponse.selector.list('.devilry-qualifiesforexam-tr')), 2)

    def test_table_row_is_rendered_multiple_students(self):
        # Tests that 21 rows are rendered, one for the table header and twenty(one for each student)
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent', period=testperiod, _quantity=20)
        teststatus = mommy.make('devilry_qualifiesforexam.Status', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'statusid': teststatus.id
            },
            sessionmock={
                'qualifying_assignmentids': [],
                'passing_relatedstudentids': [],
                'plugintypeid': 'someplugin_id'
            })
        self.assertEquals(len(mockresponse.selector.list('.devilry-qualifiesforexam-tr')), 21)

    def test_table_data_studentinfo_is_rendered(self):
        # Tests that a td element of class 'devilry-qualifiesforexam-cell-studentinfo' is rendered.
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent', period=testperiod)
        teststatus = mommy.make('devilry_qualifiesforexam.Status', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'statusid': teststatus.id
            },
            sessionmock={
                'qualifying_assignmentids': [],
                'passing_relatedstudentids': [],
                'plugintypeid': 'someplugin_id'
            })
        self.assertEquals(len(mockresponse.selector.list('.devilry-qualifiesforexam-cell-studentinfo')), 1)

    def test_table_data_qualify_result_is_rendered(self):
        # Tests that a td element of class 'devilry-qualifiesforexam-cell-qualify' is rendered.
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent', period=testperiod)
        teststatus = mommy.make('devilry_qualifiesforexam.Status', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'statusid': teststatus.id
            },
            sessionmock={
                'qualifying_assignmentids': [],
                'passing_relatedstudentids': [],
                'plugintypeid': 'someplugin_id'
            })
        self.assertEquals(len(mockresponse.selector.list('.devilry-qualifiesforexam-cell-qualify')), 1)

    def test_table_header_cell_data(self):
        # Test a more complete example of data contained in cells for two students, one qualifying and one not.
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent', period=testperiod)
        teststatus = mommy.make('devilry_qualifiesforexam.Status', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'statusid': teststatus.id
            },
            sessionmock={
                'qualifying_assignmentids': [],
                'passing_relatedstudentids': [],
                'plugintypeid': 'someplugin_id'
            })
        table_headers = mockresponse.selector.list('.devilry-qualifiesforexam-th')
        self.assertEquals(table_headers[0].alltext_normalized, 'Student')
        self.assertEquals(table_headers[1].alltext_normalized, 'Qualified for final exams')

    def test_table_student_row_data_student_does_not_qualify(self):
        # Test a more complete example of data contained in cells for two students, one qualifying and one not.
        testperiod = mommy.make('core.Period')
        relatedstudent = mommy.make('core.RelatedStudent',
                                    period=testperiod,
                                    user=mommy.make(settings.AUTH_USER_MODEL,
                                                    fullname='Jane Doe',
                                                    shortname='janedoe'))
        teststatus = mommy.make('devilry_qualifiesforexam.Status', period=testperiod)
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   status=teststatus,
                   relatedstudent=relatedstudent,
                   qualifies=False)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'statusid': teststatus.id
            },
            sessionmock={
                'qualifying_assignmentids': [],
                'passing_relatedstudentids': [],
                'plugintypeid': 'someplugin_id'
            })
        studentinfo = mockresponse.selector.one('.devilry-qualifiesforexam-cell-studentinfo')
        self.assertEquals(studentinfo.alltext_normalized, '{} {}'.format(relatedstudent.user.fullname,
                                                                         relatedstudent.user.shortname))
        self.assertEquals(mockresponse.selector.one('.devilry-qualifiesforexam-cell-qualify').alltext_normalized, 'NO')

    def test_table_student_row_data_student_qualifies(self):
        # Test a more complete example of data contained in cells for two students, one qualifying and one not.
        testperiod = mommy.make('core.Period')
        relatedstudent = mommy.make('core.RelatedStudent',
                                    period=testperiod,
                                    user=mommy.make(settings.AUTH_USER_MODEL,
                                                    fullname='Jane Doe',
                                                    shortname='janedoe'))
        teststatus = mommy.make('devilry_qualifiesforexam.Status', period=testperiod)
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   status=teststatus,
                   relatedstudent=relatedstudent,
                   qualifies=True)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'statusid': teststatus.id
            },
            sessionmock={
                'qualifying_assignmentids': [],
                'passing_relatedstudentids': [relatedstudent.id],
                'plugintypeid': 'someplugin_id'
            })
        studentinfo = mockresponse.selector.one('.devilry-qualifiesforexam-cell-studentinfo')
        self.assertEquals(studentinfo.alltext_normalized, '{} {}'.format(relatedstudent.user.fullname,
                                                                         relatedstudent.user.shortname))
        self.assertEquals(mockresponse.selector.one('.devilry-qualifiesforexam-cell-qualify').alltext_normalized, 'YES')
