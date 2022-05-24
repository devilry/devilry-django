from django import test
from django.conf import settings
from django.utils import timezone
from django.test import override_settings
from datetime import timedelta
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.devilry_account.crapps import account


class TestIndexView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = account.index.IndexView

    def test_get_title(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL,
                                 shortname='test',
                                 fullname='Test')
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=requestuser)
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized,
                         'Test (test) - Account')

    def test_get_h1(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=requestuser)
        self.assertEqual(mockresponse.selector.one('.test-primary-h1').alltext_normalized,
                         'Account overview')

    def test_get_fullname_none(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=requestuser)
        self.assertEqual(mockresponse.selector.one('.test-fullname').alltext_normalized,
                         'Name not registered for account')

    def test_get_fullname(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL,
                                 fullname='Test User')
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=requestuser)
        self.assertEqual(mockresponse.selector.one('.test-fullname').alltext_normalized,
                         'Test User')

    def test_get_shortname(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL,
                                 shortname='testuser')
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=requestuser)
        self.assertEqual(mockresponse.selector.one('.test-shortname').alltext_normalized,
                         'testuser')

    def _get_emails_from_selector(self, selector):
        return [element.alltext_normalized for element in selector.list('.test-email')]

    def test_get_email_addresses_single(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.UserEmail', email='test@example.com',
                   user=requestuser)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=requestuser)
        self.assertEqual(self._get_emails_from_selector(mockresponse.selector),
                         ['test@example.com'])
        self.assertEqual(mockresponse.selector.one('.test-emails-title').alltext_normalized,
                         'Email address')

    def test_get_email_addresses_multiple(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.UserEmail', email='test1@example.com',
                   user=requestuser)
        baker.make('devilry_account.UserEmail', email='test2@example.com',
                   user=requestuser, use_for_notifications=False)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=requestuser)
        self.assertEqual(set(self._get_emails_from_selector(mockresponse.selector)),
                         {'test1@example.com (use for notifications)', 'test2@example.com'})
        self.assertEqual(mockresponse.selector.one('.test-emails-title').alltext_normalized,
                         'Email addresses')

    def _get_usernames_from_selector(self, selector):
        return [element.alltext_normalized for element in selector.list('.test-username')]

    @override_settings(CRADMIN_LEGACY_USE_EMAIL_AUTH_BACKEND=True)
    def test_get_usernames_email_auth_backend_true(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.UserName', username='test',
                   user=requestuser)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=requestuser)
        self.assertFalse(mockresponse.selector.exists('.test-usernames-title'))
        self.assertFalse(mockresponse.selector.exists('.test-username'))

    @override_settings(CRADMIN_LEGACY_USE_EMAIL_AUTH_BACKEND=False)
    def test_get_usernames_single(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.UserName', username='test',
                   user=requestuser)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=requestuser)
        self.assertEqual(self._get_usernames_from_selector(mockresponse.selector),
                         ['test'])
        self.assertEqual(mockresponse.selector.one('.test-usernames-title').alltext_normalized,
                         'Username')

    @override_settings(CRADMIN_LEGACY_USE_EMAIL_AUTH_BACKEND=False)
    def test_get_usernames_multiple(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.UserName', username='test1',
                   user=requestuser)
        baker.make('devilry_account.UserName', username='test2',
                   user=requestuser)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=requestuser)
        self.assertEqual(set(self._get_usernames_from_selector(mockresponse.selector)),
                         {'test1', 'test2'})
        self.assertEqual(mockresponse.selector.one('.test-usernames-title').alltext_normalized,
                         'Usernames')

    def __make_period_and_semester(self, subject_longname, subject_shortname, period_longname, period_shortname, relative_to_datetime, active=True):
        if active:
            start_time = relative_to_datetime - timedelta(days=30)
            end_time = relative_to_datetime + timedelta(days=30)
        else:
            start_time = relative_to_datetime + timedelta(days=30)
            end_time = relative_to_datetime + timedelta(days=60)
        period = baker.make('core.Period',
            parentnode=baker.make('core.Subject', long_name=subject_longname, short_name=subject_shortname),
            long_name=period_longname,
            short_name=period_shortname,
            start_time=start_time,
            end_time=end_time
        )
        return period

    def test_no_role_no_active_semester(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.UserEmail', email='test@example.com', user=requestuser)
        self.__make_period_and_semester(
            subject_longname='Subject', subject_shortname='subject', 
            period_longname='Period', period_shortname='period',
            relative_to_datetime=timezone.now(), active=False
        )
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
            mockresponse.selector.one('.test-no-roles-message').alltext_normalized,
            'You are not currently assigned student and/or examiner roles on active semesters'
        )

    def test_no_role_active_semester(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.UserEmail', email='test@example.com', user=requestuser)
        self.__make_period_and_semester(
            subject_longname='Subject', subject_shortname='subject', 
            period_longname='Period', period_shortname='period',
            relative_to_datetime=timezone.now()
        )
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
            mockresponse.selector.one('.test-no-roles-message').alltext_normalized,
            'You are not currently assigned student and/or examiner roles on active semesters'
        )
    
    def test_inactive_role_active_semester_examiner(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.UserEmail', email='test@example.com', user=requestuser)
        period = self.__make_period_and_semester(
            subject_longname='Subject1', subject_shortname='subject1', 
            period_longname=f'Semester1', period_shortname=f'semester1',
            relative_to_datetime=timezone.now()
        )
        baker.make('core.RelatedExaminer', user=requestuser, period=period, active=False)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
            mockresponse.selector.one('.test-no-roles-message').alltext_normalized,
            'You are not currently assigned student and/or examiner roles on active semesters'
        )

    def test_role_examiner_no_active_semester(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.UserEmail', email='test@example.com', user=requestuser)
        period = self.__make_period_and_semester(
            subject_longname='Subject', subject_shortname='subject', 
            period_longname='Period', period_shortname='period',
            relative_to_datetime=timezone.now(), active=False
        )
        baker.make('core.RelatedExaminer', user=requestuser, period=period)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
            mockresponse.selector.one('.test-no-roles-message').alltext_normalized,
            'You are not currently assigned student and/or examiner roles on active semesters'
        )
    
    def test_inactive_role_active_semester_student(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.UserEmail', email='test@example.com', user=requestuser)
        period = self.__make_period_and_semester(
            subject_longname='Subject1', subject_shortname='subject1', 
            period_longname=f'Semester1', period_shortname=f'semester1',
            relative_to_datetime=timezone.now()
        )
        baker.make('core.RelatedStudent', user=requestuser, period=period, active=False)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
            mockresponse.selector.one('.test-no-roles-message').alltext_normalized,
            'You are not currently assigned student and/or examiner roles on active semesters'
        )
    
    def test_role_student_no_active_semester(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.UserEmail', email='test@example.com', user=requestuser)
        period = self.__make_period_and_semester(
            subject_longname='Subject', subject_shortname='subject', 
            period_longname='Period', period_shortname='period',
            relative_to_datetime=timezone.now(), active=False
        )
        baker.make('core.RelatedStudent', user=requestuser, period=period)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
            mockresponse.selector.one('.test-no-roles-message').alltext_normalized,
            'You are not currently assigned student and/or examiner roles on active semesters'
        )

    def test_role_active_semester_examiner_single_semester(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.UserEmail', email='test@example.com', user=requestuser)
        period = self.__make_period_and_semester(
            subject_longname='Subject1', subject_shortname='subject1', 
            period_longname=f'Semester1', period_shortname=f'semester1',
            relative_to_datetime=timezone.now()
        )
        baker.make('core.RelatedExaminer', user=requestuser, period=period)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertFalse(mockresponse.selector.exists('.test-student-role-heading'))
        self.assertEqual(
            mockresponse.selector.one('.test-examiner-role-heading').alltext_normalized,
            'As examiner'
        )
        roleperiodlist = mockresponse.selector.list('.test-examiner-role-list-item')
        self.assertEqual(len(roleperiodlist), 1)
        self.assertEqual(
            roleperiodlist[0].alltext_normalized,
            f'{period.parentnode.long_name}: {period.long_name}'
        )

    def test_role_active_semester_examiner_multiple_semesters(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.UserEmail', email='test@example.com', user=requestuser)
        period1 = self.__make_period_and_semester(
            subject_longname='Subject1', subject_shortname='subject1', 
            period_longname=f'Semester1', period_shortname=f'semester1',
            relative_to_datetime=timezone.now()
        )
        period2 = self.__make_period_and_semester(
            subject_longname='Subject2', subject_shortname='subject2', 
            period_longname=f'Semester1', period_shortname=f'semester1',
            relative_to_datetime=timezone.now()
        )
        baker.make('core.RelatedExaminer', user=requestuser, period=period1)
        baker.make('core.RelatedExaminer', user=requestuser, period=period2)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertFalse(mockresponse.selector.exists('.test-student-role-heading'))
        self.assertEqual(
            mockresponse.selector.one('.test-examiner-role-heading').alltext_normalized,
            'As examiner'
        )
        roleperiodlist = mockresponse.selector.list('.test-examiner-role-list-item')
        self.assertEqual(len(roleperiodlist), 2)
        self.assertEqual(
            roleperiodlist[0].alltext_normalized,
            f'{period1.parentnode.long_name}: {period1.long_name}'
        )
        self.assertEqual(
            roleperiodlist[1].alltext_normalized,
            f'{period2.parentnode.long_name}: {period2.long_name}'
        )

    def test_role_active_semester_student_single_semester(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.UserEmail', email='test@example.com', user=requestuser)
        period = self.__make_period_and_semester(
            subject_longname='Subject1', subject_shortname='subject1', 
            period_longname=f'Semester1', period_shortname=f'semester1',
            relative_to_datetime=timezone.now()
        )
        baker.make('core.RelatedStudent', user=requestuser, period=period)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertFalse(mockresponse.selector.exists('.test-examiner-role-heading'))
        self.assertEqual(
            mockresponse.selector.one('.test-student-role-heading').alltext_normalized,
            'As student'
        )
        roleperiodlist = mockresponse.selector.list('.test-student-role-list-item')
        self.assertEqual(len(roleperiodlist), 1)
        self.assertEqual(
            roleperiodlist[0].alltext_normalized,
            f'{period.parentnode.long_name}: {period.long_name}'
        )
    
    def test_role_active_semester_student_multiple_semesters(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.UserEmail', email='test@example.com', user=requestuser)
        period1 = self.__make_period_and_semester(
            subject_longname='Subject1', subject_shortname='subject1', 
            period_longname=f'Semester1', period_shortname=f'semester1',
            relative_to_datetime=timezone.now()
        )
        period2 = self.__make_period_and_semester(
            subject_longname='Subject2', subject_shortname='subject2', 
            period_longname=f'Semester1', period_shortname=f'semester1',
            relative_to_datetime=timezone.now()
        )
        baker.make('core.RelatedStudent', user=requestuser, period=period1)
        baker.make('core.RelatedStudent', user=requestuser, period=period2)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertFalse(mockresponse.selector.exists('.test-examiner-role-heading'))
        self.assertEqual(
            mockresponse.selector.one('.test-student-role-heading').alltext_normalized,
            'As student'
        )
        roleperiodlist = mockresponse.selector.list('.test-student-role-list-item')
        self.assertEqual(len(roleperiodlist), 2)
        self.assertEqual(
            roleperiodlist[0].alltext_normalized,
            f'{period1.parentnode.long_name}: {period1.long_name}'
        )
        self.assertEqual(
            roleperiodlist[1].alltext_normalized,
            f'{period2.parentnode.long_name}: {period2.long_name}'
        )

    def test_role_active_semester_examiner_and_student(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('devilry_account.UserEmail', email='test@example.com', user=requestuser)
        period1 = self.__make_period_and_semester(
            subject_longname='Subject1', subject_shortname='subject1', 
            period_longname=f'Semester1', period_shortname=f'semester1',
            relative_to_datetime=timezone.now()
        )
        baker.make('core.RelatedExaminer', user=requestuser, period=period1)
        period2 = self.__make_period_and_semester(
            subject_longname='Subject2', subject_shortname='subject2', 
            period_longname=f'Semester1', period_shortname=f'semester1',
            relative_to_datetime=timezone.now()
        )
        baker.make('core.RelatedStudent', user=requestuser, period=period2)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
            mockresponse.selector.one('.test-examiner-role-heading').alltext_normalized,
            'As examiner'
        )
        roleperiodlist_examiner = mockresponse.selector.list('.test-examiner-role-list-item')
        self.assertEqual(len(roleperiodlist_examiner), 1)
        self.assertEqual(
            roleperiodlist_examiner[0].alltext_normalized,
            f'{period1.parentnode.long_name}: {period1.long_name}'
        )
        self.assertEqual(
            mockresponse.selector.one('.test-student-role-heading').alltext_normalized,
            'As student'
        )
        roleperiodlist_student = mockresponse.selector.list('.test-student-role-list-item')
        self.assertEqual(len(roleperiodlist_student), 1)
        self.assertEqual(
            roleperiodlist_student[0].alltext_normalized,
            f'{period2.parentnode.long_name}: {period2.long_name}'
        )
