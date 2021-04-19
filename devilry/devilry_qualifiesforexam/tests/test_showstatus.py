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


class TestQualificationStatusView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = qualification_preview_view.QualificationStatusView

    def test_get(self):
        testperiod = baker.make('core.Period')
        teststatus = baker.make('devilry_qualifiesforexam.Status', period=testperiod)
        mockresponse = self.mock_getrequest(
                cradmin_role=testperiod,
                viewkwargs={
                    'statusid': teststatus.id
                })
        self.assertEqual(mockresponse.response.status_code, 200)

    def test_get_retracted_message(self):
        testperiod = baker.make('core.Period')
        teststatus = baker.make('devilry_qualifiesforexam.Status',
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
        self.assertEqual(retracted_message_element.alltext_normalized, 'retracted')

    def test_get_back_button(self):
        testperiod = baker.make('core.Period')
        teststatus = baker.make('devilry_qualifiesforexam.Status', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                viewkwargs={
                    'statusid': teststatus.id
                })
        self.assertTrue(mockresponse.selector.one('#devilry_qualifiesforexam_back_index_button'))

    def test_get_retract_button_link(self):
        testperiod = baker.make('core.Period')
        teststatus = baker.make('devilry_qualifiesforexam.Status', period=testperiod, status=status_models.Status.READY)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                viewkwargs={
                    'statusid': teststatus.id
                })
        self.assertTrue(mockresponse.selector.one('#devilry_qualifiesforexam_retract_link'))

    def test_no_retract_button_when_status_is_not_ready(self):
        testperiod = baker.make('core.Period')
        teststatus = baker.make('devilry_qualifiesforexam.Status', period=testperiod,
                                status=status_models.Status.NOTREADY)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                viewkwargs={
                    'statusid': teststatus.id
                })
        self.assertFalse(mockresponse.selector.exists('#devilry_qualifiesforexam_retract_link'))

    def test_get_print_button_link(self):
        testperiod = baker.make('core.Period')
        teststatus = baker.make('devilry_qualifiesforexam.Status', period=testperiod, status=status_models.Status.READY)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                viewkwargs={
                    'statusid': teststatus.id
                })
        self.assertTrue(mockresponse.selector.one('#devilry_qualifiesforexam_print_link'))

    def test_no_print_button_when_status_is_not_ready(self):
        testperiod = baker.make('core.Period')
        teststatus = baker.make('devilry_qualifiesforexam.Status', period=testperiod,
                                status=status_models.Status.NOTREADY)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                viewkwargs={
                    'statusid': teststatus.id
                })
        self.assertFalse(mockresponse.selector.exists('#devilry_qualifiesforexam_print_link'))

    def test_num_queries(self):
        testperiod = baker.make('core.Period')
        admin_user = baker.make(settings.AUTH_USER_MODEL)
        teststatus = baker.make('devilry_qualifiesforexam.Status',
                                period=testperiod,
                                status=status_models.Status.READY,
                                user=admin_user,
                                plugin='someplugin')
        baker.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   status=teststatus,
                   qualifies=True,
                   _quantity=10)
        baker.make('devilry_qualifiesforexam.QualifiesForFinalExam',
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
        testperiod = baker.make('core.Period')
        baker.make('core.RelatedStudent', period=testperiod)
        teststatus = baker.make('devilry_qualifiesforexam.Status', period=testperiod)
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
        testperiod = baker.make('core.Period')
        baker.make('core.RelatedStudent', period=testperiod)
        teststatus = baker.make('devilry_qualifiesforexam.Status', period=testperiod)
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
        self.assertEqual(len(mockresponse.selector.list('.devilry-qualifiesforexam-tr')), 2)

    def test_table_row_is_rendered_multiple_students(self):
        # Tests that 21 rows are rendered, one for the table header and twenty(one for each student)
        testperiod = baker.make('core.Period')
        baker.make('core.RelatedStudent', period=testperiod, _quantity=20)
        teststatus = baker.make('devilry_qualifiesforexam.Status', period=testperiod)
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
        self.assertEqual(len(mockresponse.selector.list('.devilry-qualifiesforexam-tr')), 21)

    def test_table_data_studentinfo_is_rendered(self):
        # Tests that a td element of class 'devilry-qualifiesforexam-cell-studentinfo' is rendered.
        testperiod = baker.make('core.Period')
        baker.make('core.RelatedStudent', period=testperiod)
        teststatus = baker.make('devilry_qualifiesforexam.Status', period=testperiod)
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
        self.assertEqual(len(mockresponse.selector.list('.devilry-qualifiesforexam-cell-studentinfo')), 1)

    def test_table_data_qualify_result_is_rendered(self):
        # Tests that a td element of class 'devilry-qualifiesforexam-cell-qualify' is rendered.
        testperiod = baker.make('core.Period')
        baker.make('core.RelatedStudent', period=testperiod)
        teststatus = baker.make('devilry_qualifiesforexam.Status', period=testperiod)
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
        self.assertEqual(len(mockresponse.selector.list('.devilry-qualifiesforexam-cell-qualify')), 1)

    def test_table_header_cell_data(self):
        # Test a more complete example of data contained in cells for two students, one qualifying and one not.
        testperiod = baker.make('core.Period')
        baker.make('core.RelatedStudent', period=testperiod)
        teststatus = baker.make('devilry_qualifiesforexam.Status', period=testperiod)
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
        self.assertEqual(table_headers[0].alltext_normalized, 'Student')
        self.assertEqual(table_headers[1].alltext_normalized, 'Qualified for final exams')

    def test_table_student_row_data_student_does_not_qualify(self):
        # Test a more complete example of data contained in cells for two students, one qualifying and one not.
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent',
                                    period=testperiod,
                                    user=baker.make(settings.AUTH_USER_MODEL,
                                                    fullname='Jane Doe',
                                                    shortname='janedoe'))
        teststatus = baker.make('devilry_qualifiesforexam.Status', period=testperiod)
        baker.make('devilry_qualifiesforexam.QualifiesForFinalExam',
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
        self.assertEqual(studentinfo.alltext_normalized, '{} {}'.format(relatedstudent.user.fullname,
                                                                         relatedstudent.user.shortname))
        self.assertEqual(mockresponse.selector.one('.devilry-qualifiesforexam-cell-qualify').alltext_normalized, 'NO')

    def test_table_student_row_data_student_qualifies(self):
        # Test a more complete example of data contained in cells for two students, one qualifying and one not.
        testperiod = baker.make('core.Period')
        relatedstudent = baker.make('core.RelatedStudent',
                                    period=testperiod,
                                    user=baker.make(settings.AUTH_USER_MODEL,
                                                    fullname='Jane Doe',
                                                    shortname='janedoe'))
        teststatus = baker.make('devilry_qualifiesforexam.Status', period=testperiod)
        baker.make('devilry_qualifiesforexam.QualifiesForFinalExam',
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
        self.assertEqual(studentinfo.alltext_normalized, '{} {}'.format(relatedstudent.user.fullname,
                                                                         relatedstudent.user.shortname))
        self.assertEqual(mockresponse.selector.one('.devilry-qualifiesforexam-cell-qualify').alltext_normalized, 'YES')

    def __make_related_student(self, period, fullname, lastname, shortname, candidate_id=None):
        user = baker.make(settings.AUTH_USER_MODEL, fullname=fullname, lastname=lastname, shortname=shortname)
        relatedstudent = baker.make('core.RelatedStudent', period=period, user=user, candidate_id=candidate_id)
        return relatedstudent

    def __make_qualification_item(self, status, relatedstudent, qualifies=True):
        return baker.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                          status=status, relatedstudent=relatedstudent, qualifies=qualifies)

    def test_table_default_ordering_lastname(self):
        testperiod = baker.make('core.Period')
        relatedstudent1 = self.__make_related_student(
            period=testperiod, fullname='A C', lastname='C', shortname='ac@example.com')
        relatedstudent2 = self.__make_related_student(
            period=testperiod, fullname='B B', lastname='B', shortname='bb@example.com')
        relatedstudent3 = self.__make_related_student(
            period=testperiod, fullname='C A', lastname='A', shortname='ca@example.com')

        teststatus = baker.make('devilry_qualifiesforexam.Status', period=testperiod)
        self.__make_qualification_item(teststatus, relatedstudent1)
        self.__make_qualification_item(teststatus, relatedstudent2)
        self.__make_qualification_item(teststatus, relatedstudent3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'statusid': teststatus.id
            })
        student_list = mockresponse.selector.list('.devilry-qualifiesforexam-cell-studentinfo')
        self.assertEqual(len(student_list), 3)
        self.assertEqual(student_list[0].alltext_normalized, 'C A ca@example.com')
        self.assertEqual(student_list[1].alltext_normalized, 'B B bb@example.com')
        self.assertEqual(student_list[2].alltext_normalized, 'A C ac@example.com')

    def test_table_default_ordering_lastname_if_order_by_param_is_not_supported(self):
        testperiod = baker.make('core.Period')
        relatedstudent1 = self.__make_related_student(
            period=testperiod, fullname='A C', lastname='C', shortname='ac@example.com')
        relatedstudent2 = self.__make_related_student(
            period=testperiod, fullname='B B', lastname='B', shortname='bb@example.com')
        relatedstudent3 = self.__make_related_student(
            period=testperiod, fullname='C A', lastname='A', shortname='ca@example.com')

        teststatus = baker.make('devilry_qualifiesforexam.Status', period=testperiod)
        self.__make_qualification_item(teststatus, relatedstudent1)
        self.__make_qualification_item(teststatus, relatedstudent2)
        self.__make_qualification_item(teststatus, relatedstudent3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'statusid': teststatus.id
            },
            requestkwargs={'data': {'order_by': 'asd'}})
        student_list = mockresponse.selector.list('.devilry-qualifiesforexam-cell-studentinfo')
        self.assertEqual(len(student_list), 3)
        self.assertEqual(student_list[0].alltext_normalized, 'C A ca@example.com')
        self.assertEqual(student_list[1].alltext_normalized, 'B B bb@example.com')
        self.assertEqual(student_list[2].alltext_normalized, 'A C ac@example.com')

    def test_table_order_by_lastname_sanity(self):
        testperiod = baker.make('core.Period')
        relatedstudent1 = self.__make_related_student(
            period=testperiod, fullname='A C', lastname='C', shortname='ac@example.com')
        relatedstudent2 = self.__make_related_student(
            period=testperiod, fullname='B B', lastname='B', shortname='bb@example.com')
        relatedstudent3 = self.__make_related_student(
            period=testperiod, fullname='C A', lastname='A', shortname='ca@example.com')

        teststatus = baker.make('devilry_qualifiesforexam.Status', period=testperiod)
        self.__make_qualification_item(teststatus, relatedstudent1)
        self.__make_qualification_item(teststatus, relatedstudent2)
        self.__make_qualification_item(teststatus, relatedstudent3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'statusid': teststatus.id
            },
            requestkwargs={'data': {'order_by': 'lastname'}})
        student_list = mockresponse.selector.list('.devilry-qualifiesforexam-cell-studentinfo')
        self.assertEqual(len(student_list), 3)
        self.assertEqual(student_list[0].alltext_normalized, 'C A ca@example.com')
        self.assertEqual(student_list[1].alltext_normalized, 'B B bb@example.com')
        self.assertEqual(student_list[2].alltext_normalized, 'A C ac@example.com')

    def test_table_order_by_username(self):
        testperiod = baker.make('core.Period')
        relatedstudent1 = self.__make_related_student(
            period=testperiod, fullname='C A', lastname='A', shortname='ca@example.com')
        relatedstudent2 = self.__make_related_student(
            period=testperiod, fullname='B B', lastname='B', shortname='bb@example.com')
        relatedstudent3 = self.__make_related_student(
            period=testperiod, fullname='A C', lastname='C', shortname='ac@example.com')

        teststatus = baker.make('devilry_qualifiesforexam.Status', period=testperiod)
        self.__make_qualification_item(teststatus, relatedstudent1)
        self.__make_qualification_item(teststatus, relatedstudent2)
        self.__make_qualification_item(teststatus, relatedstudent3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'statusid': teststatus.id
            },
            requestkwargs={'data': {'order_by': 'username'}})
        student_list = mockresponse.selector.list('.devilry-qualifiesforexam-cell-studentinfo')
        self.assertEqual(len(student_list), 3)
        self.assertEqual(student_list[0].alltext_normalized, 'A C ac@example.com')
        self.assertEqual(student_list[1].alltext_normalized, 'B B bb@example.com')
        self.assertEqual(student_list[2].alltext_normalized, 'C A ca@example.com')

    def test_table_order_by_fullname(self):
        testperiod = baker.make('core.Period')
        relatedstudent1 = self.__make_related_student(
            period=testperiod, fullname='C A', lastname='A', shortname='a@example.com')
        relatedstudent2 = self.__make_related_student(
            period=testperiod, fullname='B B', lastname='B', shortname='b@example.com')
        relatedstudent3 = self.__make_related_student(
            period=testperiod, fullname='A C', lastname='C', shortname='c@example.com')

        teststatus = baker.make('devilry_qualifiesforexam.Status', period=testperiod)
        self.__make_qualification_item(teststatus, relatedstudent1)
        self.__make_qualification_item(teststatus, relatedstudent2)
        self.__make_qualification_item(teststatus, relatedstudent3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'statusid': teststatus.id
            },
            requestkwargs={'data': {'order_by': 'fullname'}})
        student_list = mockresponse.selector.list('.devilry-qualifiesforexam-cell-studentinfo')
        self.assertEqual(len(student_list), 3)
        self.assertEqual(student_list[0].alltext_normalized, 'A C c@example.com')
        self.assertEqual(student_list[1].alltext_normalized, 'B B b@example.com')
        self.assertEqual(student_list[2].alltext_normalized, 'C A a@example.com')

    def test_table_order_by_candidate_id(self):
        testperiod = baker.make('core.Period')
        relatedstudent1 = self.__make_related_student(
            period=testperiod, fullname='C C', lastname='C', shortname='c@example.com', candidate_id='1')
        relatedstudent2 = self.__make_related_student(
            period=testperiod, fullname='B B', lastname='B', shortname='b@example.com', candidate_id='3')
        relatedstudent3 = self.__make_related_student(
            period=testperiod, fullname='A A', lastname='A', shortname='a@example.com', candidate_id='2')

        teststatus = baker.make('devilry_qualifiesforexam.Status', period=testperiod)
        self.__make_qualification_item(teststatus, relatedstudent1)
        self.__make_qualification_item(teststatus, relatedstudent2)
        self.__make_qualification_item(teststatus, relatedstudent3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            viewkwargs={
                'statusid': teststatus.id
            },
            requestkwargs={'data': {'order_by': 'candidateid'}})
        student_list = mockresponse.selector.list('.devilry-qualifiesforexam-cell-studentinfo')
        self.assertEqual(len(student_list), 3)
        self.assertEqual(student_list[0].alltext_normalized, 'C C c@example.com')
        self.assertEqual(student_list[1].alltext_normalized, 'A A a@example.com')
        self.assertEqual(student_list[2].alltext_normalized, 'B B b@example.com')
