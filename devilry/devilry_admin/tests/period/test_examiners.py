from __future__ import unicode_literals
import mock
from django import test
from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core.models import RelatedExaminer
from devilry.devilry_admin.tests.common.test_bulkimport_users_common import AbstractTypeInUsersViewTestMixin
from devilry.devilry_admin.views.period import examiners


class TestOverview(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = examiners.Overview

    def __get_titles(self, selector):
        return [element.alltext_normalized
                for element in selector.list('.django-cradmin-listbuilder-itemvalue-titledescription-title')]

    def test_title(self):
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertIn('Examiners on testsubject.testperiod',
                      mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual('Examiners on testsubject.testperiod',
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
                mockresponse.selector.one('#devilry_admin_period_examiners_overview_button_add')['href'])

    def test_buttonbar_addbutton_label(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
                'Add examiners',
                mockresponse.selector.one(
                        '#devilry_admin_period_examiners_overview_button_add').alltext_normalized)

    def test_buttonbar_importbutton_link(self):
        testperiod = mommy.make('core.Period')
        mock_cradmin_app = mock.MagicMock()

        def mock_reverse_appurl(viewname, **kwargs):
            return '/{}'.format(viewname)

        mock_cradmin_app.reverse_appurl = mock_reverse_appurl
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod,
                                                          cradmin_app=mock_cradmin_app)
        self.assertEqual(
                '/importexaminers',
                mockresponse.selector.one('#devilry_admin_period_examiners_overview_button_importexaminers')['href'])

    def test_buttonbar_importbutton_label(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
                'Import examiners',
                mockresponse.selector.one(
                        '#devilry_admin_period_examiners_overview_button_importexaminers').alltext_normalized)

    def test_no_examiners_messages(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
                'You have no examiners. Use the buttons above to add examiners.',
                mockresponse.selector.one('.django-cradmin-listing-no-items-message').alltext_normalized)

    def test_default_ordering(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedExaminer', period=testperiod,
                   user__fullname='UserB')
        mommy.make('core.RelatedExaminer', period=testperiod,
                   user__shortname='usera')
        mommy.make('core.RelatedExaminer', period=testperiod,
                   user__shortname='userc')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(['usera', 'UserB', 'userc'],
                         self.__get_titles(mockresponse.selector))

    def test_only_users_from_current_period(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedExaminer', period=testperiod,
                   user__shortname='usera')
        mommy.make('core.RelatedExaminer',
                   user__shortname='fromotherperiod')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(['usera'],
                         self.__get_titles(mockresponse.selector))

    def test_inactive_relatedexaminer_sanity(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedExaminer', period=testperiod, active=False)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertFalse(
                mockresponse.selector.exists('.devilry-admin-relatedexaminer-itemvalue-active'))
        self.assertTrue(
                mockresponse.selector.exists('.devilry-admin-relatedexaminer-itemvalue-inactive'))
        self.assertFalse(
                mockresponse.selector.exists('.devilry-admin-period-active-relatedexaminer-block'))
        self.assertTrue(
                mockresponse.selector.exists('.devilry-admin-period-inactive-relatedexaminer-block'))

    def test_inactive_relatedexaminer_message(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedExaminer', period=testperiod, active=False)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
                'Inactive examiner - has no access to any assignments within the semester.',
                mockresponse.selector.one(
                        '.devilry-admin-period-inactive-relatedexaminer-message').alltext_normalized)

    def test_inactive_relatedexaminer_link_label(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedExaminer', period=testperiod, active=False)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
                'Re-activate',
                mockresponse.selector.one(
                        '.devilry-admin-period-inactive-relatedexaminer-link').alltext_normalized)

    def test_inactive_relatedexaminer_link_arialabel(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedExaminer', period=testperiod, active=False,
                   user__shortname='testuser')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
                'Re-activate testuser',
                mockresponse.selector.one(
                        '.devilry-admin-period-inactive-relatedexaminer-link')['aria-label'])

    def test_active_relatedexaminer_sanity(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedExaminer', period=testperiod, active=True)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertTrue(
                mockresponse.selector.exists('.devilry-admin-relatedexaminer-itemvalue-active'))
        self.assertFalse(
                mockresponse.selector.exists('.devilry-admin-relatedexaminer-itemvalue-inactive'))
        self.assertTrue(
                mockresponse.selector.exists('.devilry-admin-period-active-relatedexaminer-block'))
        self.assertFalse(
                mockresponse.selector.exists('.devilry-admin-period-inactive-relatedexaminer-block'))

    def test_active_relatedexaminer_link_label(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedExaminer', period=testperiod, active=True)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
                'Mark as inactive',
                mockresponse.selector.one(
                        '.devilry-admin-period-active-relatedexaminer-link').alltext_normalized)

    def test_active_relatedexaminer_link_arialabel(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedExaminer', period=testperiod, active=True,
                   user__shortname='testuser')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
                'Mark testuser as inactive',
                mockresponse.selector.one(
                        '.devilry-admin-period-active-relatedexaminer-link')['aria-label'])

    def test_querycount(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedExaminer', period=testperiod, _quantity=30)
        with self.assertNumQueries(4):
            self.mock_getrequest(cradmin_role=testperiod)


class TestDeactivateExaminerView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = examiners.DeactivateView

    def test_get_title(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        relatedexaminer = mommy.make('core.RelatedExaminer',
                                     period=testperiod,
                                     user__fullname='John Doe')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                requestuser=requestuser,
                viewkwargs={'pk': relatedexaminer.pk})
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized,
                         'Deactivate examiner: John Doe?')

    def test_get_h1(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        relatedexaminer = mommy.make('core.RelatedExaminer',
                                     period=testperiod,
                                     user__fullname='John Doe')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                requestuser=requestuser,
                viewkwargs={'pk': relatedexaminer.pk})
        self.assertEqual(mockresponse.selector.one('h1').alltext_normalized,
                         'Deactivate examiner: John Doe?')

    def test_get_confirm_message(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        relatedexaminer = mommy.make('core.RelatedExaminer',
                                     period=testperiod,
                                     user__fullname='John Doe')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                requestuser=requestuser,
                viewkwargs={'pk': relatedexaminer.pk})
        self.assertEqual(mockresponse.selector.one('.devilry-cradmin-confirmview-message').alltext_normalized,
                         'Are you sure you want to make John Doe '
                         'an inactive examiner for testsubject.testperiod? Inactive examiners '
                         'can not access any assignments within the semester. '
                         'You can re-activate a deactivated examiner at any time.')

    def test_404_if_not_relatedexaminer_on_period(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period')
        otherperiod = mommy.make('core.Period')
        relatedexaminer = mommy.make('core.RelatedExaminer',
                                     period=otherperiod)
        with self.assertRaises(Http404):
            self.mock_getrequest(
                    cradmin_role=testperiod,
                    requestuser=requestuser,
                    viewkwargs={'pk': relatedexaminer.pk})

    def test_post_deactivates(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period')
        relatedexaminer = mommy.make('core.RelatedExaminer', period=testperiod)
        self.assertTrue(relatedexaminer.active)
        self.mock_http302_postrequest(
                cradmin_role=testperiod,
                requestuser=requestuser,
                viewkwargs={'pk': relatedexaminer.pk})
        updated_relatedexaminer = RelatedExaminer.objects.get(id=relatedexaminer.id)
        self.assertFalse(updated_relatedexaminer.active)

    def test_post_success_message(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period')
        relatedexaminer = mommy.make('core.RelatedExaminer',
                                     period=testperiod,
                                     user__fullname='John Doe')
        self.assertTrue(relatedexaminer.active)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
                cradmin_role=testperiod,
                messagesmock=messagesmock,
                requestuser=requestuser,
                viewkwargs={'pk': relatedexaminer.pk})
        messagesmock.add.assert_called_once_with(
                messages.SUCCESS,
                'John Doe was deactivated.',
                '')


class TestActivateExaminerView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = examiners.ActivateView

    def test_get_title(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        relatedexaminer = mommy.make('core.RelatedExaminer',
                                     period=testperiod,
                                     user__fullname='John Doe')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                requestuser=requestuser,
                viewkwargs={'pk': relatedexaminer.pk})
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized,
                         'Re-activate examiner: John Doe?')

    def test_get_h1(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        relatedexaminer = mommy.make('core.RelatedExaminer',
                                     period=testperiod,
                                     user__fullname='John Doe')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                requestuser=requestuser,
                viewkwargs={'pk': relatedexaminer.pk})
        self.assertEqual(mockresponse.selector.one('h1').alltext_normalized,
                         'Re-activate examiner: John Doe?')

    def test_get_confirm_message(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        relatedexaminer = mommy.make('core.RelatedExaminer',
                                     period=testperiod,
                                     user__fullname='John Doe')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                requestuser=requestuser,
                viewkwargs={'pk': relatedexaminer.pk})
        self.assertEqual(mockresponse.selector.one('.devilry-cradmin-confirmview-message').alltext_normalized,
                         'Please confirm that you want to re-activate John Doe.')

    def test_404_if_not_relatedexaminer_on_period(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period')
        otherperiod = mommy.make('core.Period')
        relatedexaminer = mommy.make('core.RelatedExaminer',
                                     period=otherperiod)
        with self.assertRaises(Http404):
            self.mock_getrequest(
                    cradmin_role=testperiod,
                    requestuser=requestuser,
                    viewkwargs={'pk': relatedexaminer.pk})

    def test_post_activates(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period')
        relatedexaminer = mommy.make('core.RelatedExaminer', period=testperiod, active=False)
        self.assertFalse(relatedexaminer.active)
        self.mock_http302_postrequest(
                cradmin_role=testperiod,
                requestuser=requestuser,
                viewkwargs={'pk': relatedexaminer.pk})
        updated_relatedexaminer = RelatedExaminer.objects.get(id=relatedexaminer.id)
        self.assertTrue(updated_relatedexaminer.active)

    def test_post_success_message(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make('core.Period')
        relatedexaminer = mommy.make('core.RelatedExaminer',
                                     period=testperiod,
                                     user__fullname='John Doe')
        self.assertTrue(relatedexaminer.active)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
                cradmin_role=testperiod,
                messagesmock=messagesmock,
                requestuser=requestuser,
                viewkwargs={'pk': relatedexaminer.pk})
        messagesmock.add.assert_called_once_with(
                messages.SUCCESS,
                'John Doe was re-activated.',
                '')


class TestAddView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = examiners.AddView

    def test_get_title(self):
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod)
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized,
                         'Select the examiners you want to add to testsubject.testperiod')

    def test_get_h1(self):
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod)
        self.assertEqual(mockresponse.selector.one('h1').alltext_normalized,
                         'Select the examiners you want to add to testsubject.testperiod')

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

    def test_do_not_include_users_already_relatedexaminer(self):
        testperiod = mommy.make('core.Period')
        mommy.make(settings.AUTH_USER_MODEL,
                   fullname='Not in any period')
        mommy.make('core.RelatedExaminer',
                   period=testperiod,
                   user__fullname='Already in period')
        mommy.make('core.RelatedExaminer',
                   user__fullname='In other period')
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=mock.MagicMock(),
                                                          cradmin_role=testperiod)
        self.assertEqual(
                {'Not in any period', 'In other period'},
                set(self.__get_titles(mockresponse.selector)))

    def test_post_creates_relatedexaminers(self):
        testperiod = mommy.make('core.Period')
        examineruser = mommy.make(settings.AUTH_USER_MODEL)
        self.assertEqual(0, RelatedExaminer.objects.count())
        self.mock_http302_postrequest(
                cradmin_role=testperiod,
                requestkwargs={
                    'data': {
                        'selected_items': [str(examineruser.id)]
                    }
                })
        self.assertEqual(1, RelatedExaminer.objects.count())
        created_relatedexaminer = RelatedExaminer.objects.first()
        self.assertEqual(examineruser, created_relatedexaminer.user)
        self.assertEqual(testperiod, created_relatedexaminer.period)
        self.assertTrue(created_relatedexaminer.active)

    def test_post_multiple_users(self):
        testperiod = mommy.make('core.Period')
        examineruser1 = mommy.make(settings.AUTH_USER_MODEL)
        examineruser2 = mommy.make(settings.AUTH_USER_MODEL)
        examineruser3 = mommy.make(settings.AUTH_USER_MODEL)
        self.assertEqual(0, RelatedExaminer.objects.count())
        self.mock_http302_postrequest(
                cradmin_role=testperiod,
                requestkwargs={
                    'data': {
                        'selected_items': [str(examineruser1.id),
                                           str(examineruser2.id),
                                           str(examineruser3.id)]
                    }
                })
        self.assertEqual(3, RelatedExaminer.objects.count())

    def test_post_success_message(self):
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        examineruser1 = mommy.make(settings.AUTH_USER_MODEL,
                                   shortname='testuser')
        examineruser2 = mommy.make(settings.AUTH_USER_MODEL,
                                   fullname='Test User')
        self.assertEqual(0, RelatedExaminer.objects.count())
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
                cradmin_role=testperiod,
                messagesmock=messagesmock,
                requestkwargs={
                    'data': {
                        'selected_items': [str(examineruser1.id),
                                           str(examineruser2.id)]
                    }
                })
        messagesmock.add.assert_called_once_with(
                messages.SUCCESS,
                'Added "Test User", "testuser".',
                '')


class TestImportExaminersView(test.TestCase, AbstractTypeInUsersViewTestMixin):
    viewclass = examiners.ImportExaminersView

    def test_post_valid_with_email_backend_creates_relatedusers(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            self.mock_http302_postrequest(
                    cradmin_role=testperiod,
                    requestkwargs=dict(data={
                        'users_blob': 'test1@example.com\ntest2@example.com'
                    })
            )
            self.assertEqual(2, RelatedExaminer.objects.count())
            self.assertEqual({'test1@example.com', 'test2@example.com'},
                             {relatedexaminer.user.shortname
                              for relatedexaminer in RelatedExaminer.objects.all()})

    def test_post_valid_with_email_backend_added_message(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            messagesmock = mock.MagicMock()
            self.mock_http302_postrequest(
                    cradmin_role=testperiod,
                    messagesmock=messagesmock,
                    requestkwargs=dict(data={
                        'users_blob': 'test1@example.com\ntest2@example.com'
                    })
            )
            messagesmock.add.assert_any_call(
                    messages.SUCCESS,
                    'Added 2 new examiners to {}.'.format(testperiod.get_path()),
                    '')

    def test_post_valid_with_email_backend_none_added_message(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.UserEmail',
                   user=testuser,
                   email='test@example.com')
        mommy.make('core.RelatedExaminer',
                   period=testperiod,
                   user=testuser)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            messagesmock = mock.MagicMock()
            self.mock_http302_postrequest(
                    cradmin_role=testperiod,
                    messagesmock=messagesmock,
                    requestkwargs=dict(data={
                        'users_blob': 'test@example.com'
                    })
            )
            messagesmock.add.assert_any_call(
                    messages.WARNING,
                    'No new examiners was added.',
                    '')

    def test_post_valid_with_email_backend_existing_message(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.UserEmail',
                   user=testuser,
                   email='test@example.com')
        mommy.make('core.RelatedExaminer',
                   period=testperiod,
                   user=testuser)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            messagesmock = mock.MagicMock()
            self.mock_http302_postrequest(
                    cradmin_role=testperiod,
                    messagesmock=messagesmock,
                    requestkwargs=dict(data={
                        'users_blob': 'test@example.com'
                    })
            )
            messagesmock.add.assert_called_with(
                    messages.INFO,
                    '1 users was already examiner on {}.'.format(testperiod.get_path()),
                    '')

    def test_post_valid_with_username_backend_creates_relatedusers(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            self.mock_http302_postrequest(
                    cradmin_role=testperiod,
                    requestkwargs=dict(data={
                        'users_blob': 'test1\ntest2'
                    })
            )
            self.assertEqual(2, RelatedExaminer.objects.count())
            self.assertEqual({'test1', 'test2'},
                             {relatedexaminer.user.shortname
                              for relatedexaminer in RelatedExaminer.objects.all()})

    def test_post_valid_with_username_backend_added_message(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            messagesmock = mock.MagicMock()
            self.mock_http302_postrequest(
                    cradmin_role=testperiod,
                    messagesmock=messagesmock,
                    requestkwargs=dict(data={
                        'users_blob': 'test1\ntest2'
                    })
            )
            messagesmock.add.assert_any_call(
                    messages.SUCCESS,
                    'Added 2 new examiners to {}.'.format(testperiod.get_path()),
                    '')

    def test_post_valid_with_username_backend_none_added_message(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.UserName',
                   user=testuser,
                   username='test')
        mommy.make('core.RelatedExaminer',
                   period=testperiod,
                   user=testuser)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            messagesmock = mock.MagicMock()
            self.mock_http302_postrequest(
                    cradmin_role=testperiod,
                    messagesmock=messagesmock,
                    requestkwargs=dict(data={
                        'users_blob': 'test'
                    })
            )
            messagesmock.add.assert_any_call(
                    messages.WARNING,
                    'No new examiners was added.',
                    '')

    def test_post_valid_with_username_backend_existing_message(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.UserName',
                   user=testuser,
                   username='test')
        mommy.make('core.RelatedExaminer',
                   period=testperiod,
                   user=testuser)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            messagesmock = mock.MagicMock()
            self.mock_http302_postrequest(
                    cradmin_role=testperiod,
                    messagesmock=messagesmock,
                    requestkwargs=dict(data={
                        'users_blob': 'test'
                    })
            )
            messagesmock.add.assert_any_call(
                    messages.INFO,
                    '1 users was already examiner on {}.'.format(testperiod.get_path()),
                    '')
