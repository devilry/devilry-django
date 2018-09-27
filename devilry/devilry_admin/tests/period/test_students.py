from __future__ import unicode_literals
import mock
from django import test
from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core.models import RelatedStudent
from devilry.devilry_account.models import PermissionGroup
from devilry.devilry_admin.tests.common.test_bulkimport_users_common import AbstractTypeInUsersViewTestMixin
from devilry.devilry_admin.views.period import students


class TestOverview(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = students.Overview

    def mock_crinstance_with_devilry_role(self, devilryrole=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN):
        mock_crinstance = mock.MagicMock()
        mock_crinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mock_crinstance

    def __get_titles(self, selector):
        return [element.alltext_normalized
                for element in selector.list('.django-cradmin-listbuilder-itemvalue-titledescription-title')]

    def test_title(self):
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertIn('Students on testsubject.testperiod',
                      mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual('Students on testsubject.testperiod',
                         mockresponse.selector.one('h1').alltext_normalized)

    def test_buttonbar_addbutton_link(self):
        testperiod = mommy.make('core.Period')
        mock_cradmin_app = mock.MagicMock()

        def mock_reverse_appurl(viewname, **kwargs):
            return '/{}'.format(viewname)

        mock_cradmin_app.reverse_appurl = mock_reverse_appurl
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod,
                                                          cradmin_app=mock_cradmin_app)
        self.assertEqual(
            '/add',
            mockresponse.selector.one('#devilry_admin_period_students_overview_button_add')['href'])

    def test_buttonbar_addbutton_label(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
                'Add students',
                mockresponse.selector.one(
                        '#devilry_admin_period_students_overview_button_add').alltext_normalized)

    def test_buttonbar_importbutton_not_rendered_for_periodadmin_sanity(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.mock_crinstance_with_devilry_role(devilryrole=PermissionGroup.GROUPTYPE_PERIODADMIN),
            cradmin_role=testperiod
        )
        self.assertFalse(
            mockresponse.selector.exists('#devilry_admin_period_students_overview_button_importstudents'))

    def test_buttonbar_importbutton_not_rendered_for_subjectadmin_sanity(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.mock_crinstance_with_devilry_role(devilryrole=PermissionGroup.GROUPTYPE_SUBJECTADMIN),
            cradmin_role=testperiod
        )
        self.assertFalse(
            mockresponse.selector.exists('#devilry_admin_period_students_overview_button_importstudents'))

    def test_buttonbar_importbutton_rendered_for_departmentadmin_sanity(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.mock_crinstance_with_devilry_role(),
            cradmin_role=testperiod
        )
        self.assertTrue(
            mockresponse.selector.exists('#devilry_admin_period_students_overview_button_importstudents'))

    def test_buttonbar_importbutton_link(self):
        testperiod = mommy.make('core.Period')
        mock_cradmin_app = mock.MagicMock()

        def mock_reverse_appurl(viewname, **kwargs):
            return '/{}'.format(viewname)

        mock_cradmin_app.reverse_appurl = mock_reverse_appurl
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.mock_crinstance_with_devilry_role(),
            cradmin_role=testperiod,
            cradmin_app=mock_cradmin_app)
        self.assertEqual(
            '/importstudents',
            mockresponse.selector.one('#devilry_admin_period_students_overview_button_importstudents')['href'])

    def test_buttonbar_importbutton_label(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.mock_crinstance_with_devilry_role(),
            cradmin_role=testperiod)
        self.assertEqual(
                'Import students',
                mockresponse.selector.one(
                        '#devilry_admin_period_students_overview_button_importstudents').alltext_normalized)

    def test_no_students_messages(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
                'You have no students. Use the buttons above to add students.',
                mockresponse.selector.one('.django-cradmin-listing-no-items-message').alltext_normalized)

    def test_default_ordering(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent', period=testperiod,
                   user__shortname='b',
                   user__fullname='UserB')
        mommy.make('core.RelatedStudent', period=testperiod,
                   user__shortname='usera')
        mommy.make('core.RelatedStudent', period=testperiod,
                   user__shortname='userc')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(['usera', 'UserB(b)', 'userc'],
                         self.__get_titles(mockresponse.selector))

    def test_only_users_from_current_period(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent', period=testperiod,
                   user__shortname='usera')
        mommy.make('core.RelatedStudent',
                   user__shortname='fromotherperiod')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(['usera'],
                         self.__get_titles(mockresponse.selector))

    def test_inactive_relatedstudent_sanity(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent', period=testperiod, active=False)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertFalse(
                mockresponse.selector.exists('.devilry-admin-relatedstudent-itemvalue-active'))
        self.assertTrue(
                mockresponse.selector.exists('.devilry-admin-relatedstudent-itemvalue-inactive'))
        self.assertFalse(
                mockresponse.selector.exists('.devilry-admin-period-active-relatedstudent-block'))
        self.assertTrue(
                mockresponse.selector.exists('.devilry-admin-period-inactive-relatedstudent-block'))

    def test_inactive_relatedstudent_message(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent', period=testperiod, active=False)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
                'Inactive student - can not be added to new assignments, and can not be '
                'marked as qualified for final exams.',
                mockresponse.selector.one(
                        '.devilry-admin-period-inactive-relatedstudent-message').alltext_normalized)

    def test_inactive_relatedstudent_link_label(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent', period=testperiod, active=False)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
                'Re-activate',
                mockresponse.selector.one(
                        '.devilry-admin-period-inactive-relatedstudent-link').alltext_normalized)

    def test_inactive_relatedstudent_link_arialabel(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent', period=testperiod, active=False,
                   user__shortname='testuser')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
                'Re-activate testuser',
                mockresponse.selector.one(
                        '.devilry-admin-period-inactive-relatedstudent-link')['aria-label'])

    def test_active_relatedstudent_sanity(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent', period=testperiod, active=True)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertTrue(
                mockresponse.selector.exists('.devilry-admin-relatedstudent-itemvalue-active'))
        self.assertFalse(
                mockresponse.selector.exists('.devilry-admin-relatedstudent-itemvalue-inactive'))
        self.assertTrue(
                mockresponse.selector.exists('.devilry-admin-period-active-relatedstudent-block'))
        self.assertFalse(
                mockresponse.selector.exists('.devilry-admin-period-inactive-relatedstudent-block'))

    def test_active_relatedstudent_link_label(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent', period=testperiod, active=True)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
                'Mark as inactive',
                mockresponse.selector.one(
                        '.devilry-admin-period-active-relatedstudent-link').alltext_normalized)

    def test_active_relatedstudent_link_arialabel(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent', period=testperiod, active=True,
                   user__shortname='testuser')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
                'Mark testuser as inactive',
                mockresponse.selector.one(
                        '.devilry-admin-period-active-relatedstudent-link')['aria-label'])

    def test_querycount(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent', period=testperiod, _quantity=30)
        with self.assertNumQueries(5):
            self.mock_getrequest(cradmin_role=testperiod)


class TestDeactivateStudentView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = students.DeactivateView

    def test_get_title(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        relatedstudent = mommy.make('core.RelatedStudent',
                                    period=testperiod,
                                    user__fullname='Jane Doe')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                requestuser=requestuser,
                viewkwargs={'pk': relatedstudent.pk})
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized,
                         'Deactivate student: Jane Doe?')

    def test_get_h1(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        relatedstudent = mommy.make('core.RelatedStudent',
                                    period=testperiod,
                                    user__fullname='Jane Doe')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                requestuser=requestuser,
                viewkwargs={'pk': relatedstudent.pk})
        self.assertEqual(mockresponse.selector.one('h1').alltext_normalized,
                         'Deactivate student: Jane Doe?')

    def test_get_confirm_message(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        relatedstudent = mommy.make('core.RelatedStudent',
                                    period=testperiod,
                                    user__fullname='Jane Doe')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                requestuser=requestuser,
                viewkwargs={'pk': relatedstudent.pk})
        self.assertEqual(mockresponse.selector.one('.devilry-cradmin-confirmview-message').alltext_normalized,
                         'Are you sure you want to make Jane Doe '
                         'an inactive student for testsubject.testperiod? Inactive students '
                         'can not be added to new assignments, but they still have access '
                         'to assignments that they have already been granted access to. Inactive '
                         'students are clearly marked with warning messages throughout the student, examiner '
                         'and admin UI, but students and examiners are not notified in any way when you '
                         'deactivate a student. You can re-activate a deactivated student at any time.')

    def test_404_if_not_relatedstudent_on_period(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period')
        otherperiod = mommy.make('core.Period')
        relatedstudent = mommy.make('core.RelatedStudent',
                                    period=otherperiod)
        with self.assertRaises(Http404):
            self.mock_getrequest(
                    cradmin_role=testperiod,
                    requestuser=requestuser,
                    viewkwargs={'pk': relatedstudent.pk})

    def test_post_deactivates(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period')
        relatedstudent = mommy.make('core.RelatedStudent', period=testperiod)
        self.assertTrue(relatedstudent.active)
        self.mock_http302_postrequest(
                cradmin_role=testperiod,
                requestuser=requestuser,
                viewkwargs={'pk': relatedstudent.pk})
        updated_relatedstudent = RelatedStudent.objects.get(id=relatedstudent.id)
        self.assertFalse(updated_relatedstudent.active)

    def test_post_success_message(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period')
        relatedstudent = mommy.make('core.RelatedStudent',
                                    period=testperiod,
                                    user__fullname='Jane Doe')
        self.assertTrue(relatedstudent.active)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
                cradmin_role=testperiod,
                messagesmock=messagesmock,
                requestuser=requestuser,
                viewkwargs={'pk': relatedstudent.pk})
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'Jane Doe was deactivated.',
            '')


class TestActivateStudentView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = students.ActivateView

    def test_get_title(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        relatedstudent = mommy.make('core.RelatedStudent',
                                    period=testperiod,
                                    user__fullname='Jane Doe')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                requestuser=requestuser,
                viewkwargs={'pk': relatedstudent.pk})
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized,
                         'Re-activate student: Jane Doe?')

    def test_get_h1(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        relatedstudent = mommy.make('core.RelatedStudent',
                                    period=testperiod,
                                    user__fullname='Jane Doe')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                requestuser=requestuser,
                viewkwargs={'pk': relatedstudent.pk})
        self.assertEqual(mockresponse.selector.one('h1').alltext_normalized,
                         'Re-activate student: Jane Doe?')

    def test_get_confirm_message(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        relatedstudent = mommy.make('core.RelatedStudent',
                                    period=testperiod,
                                    user__fullname='Jane Doe')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                requestuser=requestuser,
                viewkwargs={'pk': relatedstudent.pk})
        self.assertEqual(mockresponse.selector.one('.devilry-cradmin-confirmview-message').alltext_normalized,
                         'Please confirm that you want to re-activate Jane Doe.')

    def test_404_if_not_relatedstudent_on_period(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period')
        otherperiod = mommy.make('core.Period')
        relatedstudent = mommy.make('core.RelatedStudent',
                                    period=otherperiod)
        with self.assertRaises(Http404):
            self.mock_getrequest(
                    cradmin_role=testperiod,
                    requestuser=requestuser,
                    viewkwargs={'pk': relatedstudent.pk})

    def test_post_activates(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period')
        relatedstudent = mommy.make('core.RelatedStudent', period=testperiod, active=False)
        self.assertFalse(relatedstudent.active)
        self.mock_http302_postrequest(
                cradmin_role=testperiod,
                requestuser=requestuser,
                viewkwargs={'pk': relatedstudent.pk})
        updated_relatedstudent = RelatedStudent.objects.get(id=relatedstudent.id)
        self.assertTrue(updated_relatedstudent.active)

    def test_post_success_message(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period')
        relatedstudent = mommy.make('core.RelatedStudent',
                                    period=testperiod,
                                    user__fullname='Jane Doe')
        self.assertTrue(relatedstudent.active)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
                cradmin_role=testperiod,
                messagesmock=messagesmock,
                requestuser=requestuser,
                viewkwargs={'pk': relatedstudent.pk})
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'Jane Doe was re-activated.',
            '')


class TestAddView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = students.AddView

    def test_get_title(self):
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod)
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized,
                         'Select the students you want to add to testsubject.testperiod')

    def test_get_h1(self):
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod)
        self.assertEqual(mockresponse.selector.one('h1').alltext_normalized,
                         'Select the students you want to add to testsubject.testperiod')

    def test_render_sanity(self):
        testperiod = mommy.make('core.Period')
        mommy.make(settings.AUTH_USER_MODEL,
                   fullname='Test User',
                   shortname='test@example.com')
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=mock.MagicMock(),
                                                          cradmin_role=testperiod)
        self.assertEqual(
            'Test User',
            mockresponse.selector.one(
                    '.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)
        self.assertEqual(
            'test@example.com',
            mockresponse.selector.one(
                    '.django-cradmin-listbuilder-itemvalue-titledescription-description').alltext_normalized)

    def __get_titles(self, selector):
        return [element.alltext_normalized
                for element in selector.list('.django-cradmin-listbuilder-itemvalue-titledescription-title')]

    def test_do_not_include_users_already_relatedstudent(self):
        testperiod = mommy.make('core.Period')
        mommy.make(settings.AUTH_USER_MODEL,
                   fullname='Not in any period')
        mommy.make('core.RelatedStudent',
                   period=testperiod,
                   user__fullname='Already in period')
        mommy.make('core.RelatedStudent',
                   user__fullname='In other period')
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=mock.MagicMock(),
                                                          cradmin_role=testperiod)
        self.assertEqual(
                {'Not in any period', 'In other period'},
                set(self.__get_titles(mockresponse.selector)))

    def test_post_creates_relatedstudents(self):
        testperiod = mommy.make('core.Period')
        studentuser = mommy.make(settings.AUTH_USER_MODEL)
        self.assertEqual(0, RelatedStudent.objects.count())
        self.mock_http302_postrequest(
                cradmin_role=testperiod,
                requestkwargs={
                    'data': {
                        'selected_items': [str(studentuser.id)]
                    }
                })
        self.assertEqual(1, RelatedStudent.objects.count())
        created_relatedstudent = RelatedStudent.objects.first()
        self.assertEqual(studentuser, created_relatedstudent.user)
        self.assertEqual(testperiod, created_relatedstudent.period)
        self.assertTrue(created_relatedstudent.active)

    def test_post_multiple_users(self):
        testperiod = mommy.make('core.Period')
        studentuser1 = mommy.make(settings.AUTH_USER_MODEL)
        studentuser2 = mommy.make(settings.AUTH_USER_MODEL)
        studentuser3 = mommy.make(settings.AUTH_USER_MODEL)
        self.assertEqual(0, RelatedStudent.objects.count())
        self.mock_http302_postrequest(
                cradmin_role=testperiod,
                requestkwargs={
                    'data': {
                        'selected_items': [str(studentuser1.id),
                                           str(studentuser2.id),
                                           str(studentuser3.id)]
                    }
                })
        self.assertEqual(3, RelatedStudent.objects.count())

    def test_post_success_message(self):
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        studentuser1 = mommy.make(settings.AUTH_USER_MODEL,
                                  shortname='testuser')
        studentuser2 = mommy.make(settings.AUTH_USER_MODEL,
                                  fullname='Test User')
        self.assertEqual(0, RelatedStudent.objects.count())
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
                cradmin_role=testperiod,
                messagesmock=messagesmock,
                requestkwargs={
                    'data': {
                        'selected_items': [str(studentuser1.id),
                                           str(studentuser2.id)]
                    }
                })
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'Added "Test User", "testuser".',
            '')


class TestImportStudentsView(test.TestCase, AbstractTypeInUsersViewTestMixin):
    viewclass = students.ImportStudentsView

    def test_user_devilryrole_periodadmin_raises_404(self):
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_instance=self.mock_crinstance_with_devilry_role(
                    devilryrole=PermissionGroup.GROUPTYPE_PERIODADMIN)
            )

    def test_user_devilryrole_subjectadmin_raises_404(self):
        with self.assertRaises(Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_instance=self.mock_crinstance_with_devilry_role(
                    devilryrole=PermissionGroup.GROUPTYPE_PERIODADMIN)
            )

    def test_user_devilryrole_departmentadmin_does_not_raise_404(self):
        self.mock_http200_getrequest_htmls(
            cradmin_instance=self.mock_crinstance_with_devilry_role()
        )

    def test_post_valid_with_email_backend_creates_relatedusers(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            self.mock_http302_postrequest(
                cradmin_instance=self.mock_crinstance_with_devilry_role(),
                cradmin_role=testperiod,
                requestkwargs=dict(data={
                    'users_blob': 'test1@example.com\ntest2@example.com'
                })
            )
            self.assertEqual(2, RelatedStudent.objects.count())
            self.assertEqual({'test1@example.com', 'test2@example.com'},
                             {relatedstudent.user.shortname
                              for relatedstudent in RelatedStudent.objects.all()})

    def test_post_valid_with_email_backend_added_message(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            messagesmock = mock.MagicMock()
            self.mock_http302_postrequest(
                cradmin_instance=self.mock_crinstance_with_devilry_role(),
                cradmin_role=testperiod,
                messagesmock=messagesmock,
                requestkwargs=dict(data={
                    'users_blob': 'test1@example.com\ntest2@example.com'
                })
            )
            messagesmock.add.assert_any_call(
                messages.SUCCESS,
                'Added 2 new students to {}.'.format(testperiod.get_path()),
                '')

    def test_post_valid_with_email_backend_none_added_message(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.UserEmail',
                   user=testuser,
                   email='test@example.com')
        mommy.make('core.RelatedStudent',
                   period=testperiod,
                   user=testuser)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            messagesmock = mock.MagicMock()
            self.mock_http302_postrequest(
                cradmin_instance=self.mock_crinstance_with_devilry_role(),
                cradmin_role=testperiod,
                messagesmock=messagesmock,
                requestkwargs=dict(data={
                    'users_blob': 'test@example.com'
                })
            )
            messagesmock.add.assert_any_call(
                messages.WARNING,
                'No new students was added.',
                '')

    def test_post_valid_with_email_backend_existing_message(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.UserEmail',
                   user=testuser,
                   email='test@example.com')
        mommy.make('core.RelatedStudent',
                   period=testperiod,
                   user=testuser)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            messagesmock = mock.MagicMock()
            self.mock_http302_postrequest(
                cradmin_instance=self.mock_crinstance_with_devilry_role(),
                cradmin_role=testperiod,
                messagesmock=messagesmock,
                requestkwargs=dict(data={
                    'users_blob': 'test@example.com'
                })
            )
            messagesmock.add.assert_called_with(
                messages.INFO,
                '1 users was already student on {}.'.format(testperiod.get_path()),
                '')

    def test_post_valid_with_username_backend_creates_relatedusers(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            self.mock_http302_postrequest(
                cradmin_instance=self.mock_crinstance_with_devilry_role(),
                cradmin_role=testperiod,
                requestkwargs=dict(data={
                    'users_blob': 'test1\ntest2'
                })
            )
            self.assertEqual(2, RelatedStudent.objects.count())
            self.assertEqual({'test1', 'test2'},
                             {relatedstudent.user.shortname
                              for relatedstudent in RelatedStudent.objects.all()})

    def test_post_valid_with_username_backend_added_message(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            messagesmock = mock.MagicMock()
            self.mock_http302_postrequest(
                cradmin_instance=self.mock_crinstance_with_devilry_role(),
                cradmin_role=testperiod,
                messagesmock=messagesmock,
                requestkwargs=dict(data={
                    'users_blob': 'test1\ntest2'
                })
            )
            messagesmock.add.assert_any_call(
                messages.SUCCESS,
                'Added 2 new students to {}.'.format(testperiod.get_path()),
                '')

    def test_post_valid_with_username_backend_none_added_message(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.UserName',
                   user=testuser,
                   username='test')
        mommy.make('core.RelatedStudent',
                   period=testperiod,
                   user=testuser)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            messagesmock = mock.MagicMock()
            self.mock_http302_postrequest(
                cradmin_instance=self.mock_crinstance_with_devilry_role(),
                cradmin_role=testperiod,
                messagesmock=messagesmock,
                requestkwargs=dict(data={
                    'users_blob': 'test'
                })
            )
            messagesmock.add.assert_any_call(
                messages.WARNING,
                'No new students was added.',
                '')

    def test_post_valid_with_username_backend_existing_message(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.UserName',
                   user=testuser,
                   username='test')
        mommy.make('core.RelatedStudent',
                   period=testperiod,
                   user=testuser)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            messagesmock = mock.MagicMock()
            self.mock_http302_postrequest(
                cradmin_instance=self.mock_crinstance_with_devilry_role(),
                cradmin_role=testperiod,
                messagesmock=messagesmock,
                requestkwargs=dict(data={
                    'users_blob': 'test'
                })
            )
            messagesmock.add.assert_any_call(
                messages.INFO,
                '1 users was already student on {}.'.format(testperiod.get_path()),
                '')
