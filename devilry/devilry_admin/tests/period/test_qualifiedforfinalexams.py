from django_cradmin import cradmin_testhelpers
from django import test
from django.conf import settings
from model_mommy import mommy
from devilry.devilry_admin.views.period import qualifiedforfinalexams
from devilry.devilry_qualifiesforexam.models import Status
import htmls


class TestListViewMixin(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = qualifiedforfinalexams.ListViewMixin

    def test_get_view_without_students(self):
        """
        Test for the message showed when there aren't students
        """
        subject = mommy.make('core.Subject', short_name="INF100")
        period = mommy.make('core.Period', parentnode=subject, short_name="Spring 2015")
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=period)
        view_message = mockresponse.selector.one('#objecttableview-no-items-message').alltext_normalized
        self.assertEqual("There is no students registered for "+subject.short_name+"."+period.short_name+".",
                         view_message)

    def test_get_view_with_one_student(self):
        """
        Test for getting a student
        """
        subject = mommy.make('core.Subject')
        period = mommy.make('core.Period', parentnode=subject)
        user = mommy.make('devilry_account.User', shortname="Espen Kristiansen")
        related_student = mommy.make('core.RelatedStudent', user=user, period=period)
        status = mommy.make('devilry_qualifiesforexam.Status', period=period)
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam', relatedstudent=related_student, status=status)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=period)
        view_message = mockresponse.selector.one('.devilry-user-verbose-inline-shortname').alltext_normalized
        self.assertEqual(user.shortname, view_message)

    def test_get_view_with_multiple_students_ordered(self):
        """
        Test for getting several students ordered
        """
        subject = mommy.make('core.Subject')
        period = mommy.make('core.Period', parentnode=subject)
        status = mommy.make('devilry_qualifiesforexam.Status', period=period)
        user1 = mommy.make('devilry_account.User', fullname="A")
        user2 = mommy.make('devilry_account.User', fullname="C")
        user3 = mommy.make('devilry_account.User', fullname="B")
        related_student1 = mommy.make('core.RelatedStudent', user=user1, period=period)
        related_student2 = mommy.make('core.RelatedStudent', user=user2, period=period)
        related_student3 = mommy.make('core.RelatedStudent', user=user3, period=period)
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam', relatedstudent=related_student1, status=status)
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam', relatedstudent=related_student2, status=status)
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam', relatedstudent=related_student3, status=status)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=period)
        mockresponse.selector.prettyprint()
        page_list = mockresponse.selector.list('.devilry-user-verbose-inline-fullname')
        self.assertEquals(3, len(page_list))
        self.assertEqual(user1.fullname, page_list[0].alltext_normalized)
        self.assertEqual(user2.fullname, page_list[2].alltext_normalized)
        self.assertEqual(user3.fullname, page_list[1].alltext_normalized)


class TestListViewStep3(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = qualifiedforfinalexams.ListViewStep3

    def test_get_view_title(self):
        """
        Test for the view title ('Preview and confirm').
        """
        subject = mommy.make('core.Subject')
        period = mommy.make('core.Period', parentnode=subject)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=period)
        view_title = mockresponse.selector.one('.django-cradmin-page-header-inner').alltext_normalized
        self.assertEquals('Preview and confirm', view_title)

    def test_get_confirm_button_text(self):
        """
        Test for the button for confirming a page in view ('ListViewStep3').
        """
        subject = mommy.make('core.Subject')
        period = mommy.make('core.Period', parentnode=subject)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=period)
        button_text = mockresponse.selector.one('.btn-primary').alltext_normalized
        self.assertEquals('Confirm', button_text)

    def test_post(self):
        """
        Test post request which changes the status
        """
        subject = mommy.make('core.Subject')
        period = mommy.make('core.Period', parentnode=subject)
        status = mommy.make('devilry_qualifiesforexam.Status', period=period, status=Status.NOTREADY, plugin="Test")
        self.mock_http302_postrequest(cradmin_role=period)
        status_after = Status.objects.get(id=status.id)
        self.assertEquals(status_after.status, Status.READY)


class TestListViewStep4(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = qualifiedforfinalexams.ListViewStep4

    def test_get_view_title(self):
        """
        Test for the view title ('Qualified for final exams').
        """
        subject = mommy.make('core.Subject')
        period = mommy.make('core.Period', parentnode=subject)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=period)
        view_title = mockresponse.selector.one('.django-cradmin-page-header-inner').alltext_normalized
        self.assertEquals('Qualified for final exams', view_title)

    def test_get_buttons(self):
        """
        Test for the buttons on page view ('ListViewStep4').
        """
        subject = mommy.make('core.Subject')
        period = mommy.make('core.Period', parentnode=subject)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=period)
        button_list = mockresponse.selector.list('.btn')
        self.assertEquals(3, len(button_list))
        self.assertEqual("Print", button_list[0].alltext_normalized)
        self.assertEqual("Update", button_list[1].alltext_normalized)
        self.assertEqual("Retract", button_list[2].alltext_normalized)

    # test post_method (redirects to step1 to start the process again)


class TestRetractionView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = qualifiedforfinalexams.RetractionView

    def test_post_without_required_field_message(self):
        """
        Test a post without requested field.
        """
        subject = mommy.make('core.Subject')
        period = mommy.make('core.Period', parentnode=subject)
        status = mommy.make('devilry_qualifiesforexam.Status', period=period, status=Status.READY, plugin="Test")
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=period,
            viewkwargs={'pk': status.id},
            requestkwargs={
                'data': {
                    'message': '',
                }
            }
        )
        self.assertTrue(mockresponse.selector.exists('#div_id_message.has-error'))

    def test_post_with_required_field_filled(self):
        """
        Post the field message of Status.
        """
        subject = mommy.make('core.Subject')
        period = mommy.make('core.Period', parentnode=subject)
        status = mommy.make('devilry_qualifiesforexam.Status', period=period, status=Status.READY, plugin="Test")
        self.mock_http302_postrequest(
            cradmin_role=period,
            viewkwargs={'pk': status.id},
            requestkwargs={
                'data': {
                    'message': 'test',
                }
            })
        status_after = Status.objects.get(id=status.id)
        self.assertEquals(status_after.message, 'test')


class TestPrintQualifiedStudentsView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = qualifiedforfinalexams.PrintQualifiedStudentsView

    def test_get_view_title(self):
        """
        Test for the view title.
        """
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        subject = mommy.make('core.Subject', short_name="INF100")
        period = mommy.make('core.Period', short_name="Spring 2015", parentnode=subject, admins=[requestuser])
        status = mommy.make('devilry_qualifiesforexam.Status', period=period, status=Status.READY, plugin="Test")
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period, viewkwargs={'status_id': status.id}, requestuser=requestuser
        )
        view_title = mockresponse.selector.one('h1').alltext_normalized
        self.assertEquals(view_title, subject.short_name+"."+period.short_name)

    def test_get_print_button_text(self):
        """
        Test for the button for printing the list of qualified students in view ('PrintQualifiedStudents').
        """
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        subject = mommy.make('core.Subject')
        period = mommy.make('core.Period', parentnode=subject, admins=[requestuser])
        status = mommy.make('devilry_qualifiesforexam.Status', period=period, status=Status.READY, plugin="Test")
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period, viewkwargs={'status_id': status.id}, requestuser=requestuser
        )
        button_text = mockresponse.selector.one('.btn-primary').alltext_normalized
        self.assertEquals('Print', button_text)

    def test_get_form(self):
        """
        Test that a form appears on the page view ('PrintQualifiedStudents').
        """
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        subject = mommy.make('core.Subject')
        period = mommy.make('core.Period', parentnode=subject, admins=[requestuser])
        status = mommy.make('devilry_qualifiesforexam.Status', period=period, status=Status.READY, plugin="Test")
        options = 'NameUsernameLast name'
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period, viewkwargs={'status_id': status.id}, requestuser=requestuser
        )
        form = mockresponse.selector.one('#sortby-field').alltext_normalized
        self.assertEquals(form, options)

    def test_get_students(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        subject = mommy.make('core.Subject')
        period = mommy.make('core.Period', parentnode=subject, admins=[requestuser])
        status = mommy.make('devilry_qualifiesforexam.Status', period=period, status=Status.READY, plugin="Test")
        user1 = mommy.make('devilry_account.User', fullname="A")
        user2 = mommy.make('devilry_account.User', fullname="C")
        user3 = mommy.make('devilry_account.User', fullname="B")
        related_student1 = mommy.make('core.RelatedStudent', user=user1, period=period)
        related_student2 = mommy.make('core.RelatedStudent', user=user2, period=period)
        related_student3 = mommy.make('core.RelatedStudent', user=user3, period=period)
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=related_student1,
                   status=status,
                   qualifies=True)
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=related_student2,
                   status=status,
                   qualifies=True)
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=related_student3,
                   status=status,
                   qualifies=False)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period, viewkwargs={'status_id': status.id}, requestuser=requestuser
        )
        success_labels = mockresponse.selector.list('.label-success')
        warning_labels = mockresponse.selector.list('.label-warning')
        self.assertEquals(2, len(success_labels))
        self.assertEquals(1, len(warning_labels))

    def test_get_students_ordered_by_name(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        subject = mommy.make('core.Subject')
        period = mommy.make('core.Period', parentnode=subject, admins=[requestuser])
        status = mommy.make('devilry_qualifiesforexam.Status', period=period, status=Status.READY, plugin="Test")
        user1 = mommy.make('devilry_account.User', fullname="God of Fertility", shortname="fert@example.com")
        user2 = mommy.make('devilry_account.User', fullname="Celine Redmiles", shortname="celred@example.com")
        user3 = mommy.make('devilry_account.User', fullname="April Duck", shortname="duck32@example.com")
        related_student1 = mommy.make('core.RelatedStudent', user=user1, period=period)
        related_student2 = mommy.make('core.RelatedStudent', user=user2, period=period)
        related_student3 = mommy.make('core.RelatedStudent', user=user3, period=period)
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=related_student1,
                   status=status,
                   qualifies=True)
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=related_student2,
                   status=status,
                   qualifies=True)
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=related_student3,
                   status=status,
                   qualifies=True)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period,
            viewkwargs={'status_id': status.id},
            requestuser=requestuser,
            requestkwargs={
                'data': {
                    'sortby': 'name',
                }
            }
        )
        student_list = mockresponse.selector.list('.fullname')
        self.assertEquals(3, len(student_list))
        self.assertEqual(student_list[0].alltext_normalized, user3.fullname)
        self.assertEqual(student_list[1].alltext_normalized, user2.fullname)
        self.assertEqual(student_list[2].alltext_normalized, user1.fullname)

    def test_get_students_ordered_by_lastname(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        subject = mommy.make('core.Subject')
        period = mommy.make('core.Period', parentnode=subject, admins=[requestuser])
        status = mommy.make('devilry_qualifiesforexam.Status', period=period, status=Status.READY, plugin="Test")
        user1 = mommy.make('devilry_account.User', fullname="God of Fertility", lastname="Fertility")
        user2 = mommy.make('devilry_account.User', fullname="Celine Redmiles", lastname="Redmiles")
        user3 = mommy.make('devilry_account.User', fullname="April Duck", lastname="Duck")
        related_student1 = mommy.make('core.RelatedStudent', user=user1, period=period)
        related_student2 = mommy.make('core.RelatedStudent', user=user2, period=period)
        related_student3 = mommy.make('core.RelatedStudent', user=user3, period=period)
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=related_student1,
                   status=status,
                   qualifies=True)
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=related_student2,
                   status=status,
                   qualifies=True)
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=related_student3,
                   status=status,
                   qualifies=True)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period,
            viewkwargs={'status_id': status.id},
            requestuser=requestuser,
            requestkwargs={
                'data': {
                    'sortby': 'lastname',
                }
            }
        )
        student_list = mockresponse.selector.list('.fullname')
        self.assertEquals(3, len(student_list))
        self.assertEqual(student_list[0].alltext_normalized, user3.fullname)
        self.assertEqual(student_list[1].alltext_normalized, user1.fullname)
        self.assertEqual(student_list[2].alltext_normalized, user2.fullname)

    def test_get_students_ordered_by_username(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        subject = mommy.make('core.Subject')
        period = mommy.make('core.Period', parentnode=subject, admins=[requestuser])
        status = mommy.make('devilry_qualifiesforexam.Status', period=period, status=Status.READY, plugin="Test")
        user1 = mommy.make('devilry_account.User', fullname="God of Fertility", shortname="fert@example.com")
        user2 = mommy.make('devilry_account.User', fullname="Celine Redmiles", shortname="celred@example.com")
        user3 = mommy.make('devilry_account.User', fullname="April Duck", shortname="guck32@example.com")
        related_student1 = mommy.make('core.RelatedStudent', user=user1, period=period)
        related_student2 = mommy.make('core.RelatedStudent', user=user2, period=period)
        related_student3 = mommy.make('core.RelatedStudent', user=user3, period=period)
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=related_student1,
                   status=status,
                   qualifies=True)
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=related_student2,
                   status=status,
                   qualifies=True)
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=related_student3,
                   status=status,
                   qualifies=True)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=period,
            viewkwargs={'status_id': status.id},
            requestuser=requestuser,
            requestkwargs={
                'data': {
                    'sortby': 'username',
                }
            }
        )
        student_list = mockresponse.selector.list('.fullname')
        self.assertEquals(3, len(student_list))
        self.assertEqual(student_list[0].alltext_normalized, user2.fullname)
        self.assertEqual(student_list[1].alltext_normalized, user1.fullname)
        self.assertEqual(student_list[2].alltext_normalized, user3.fullname)

