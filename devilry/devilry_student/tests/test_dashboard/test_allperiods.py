from __future__ import unicode_literals

from datetime import timedelta

from django import test
from django.conf import settings
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core.mommy_recipes import OLD_PERIOD_START, ACTIVE_PERIOD_START
from devilry.devilry_student.views.dashboard import allperiods


class TestAllPeriodsView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = allperiods.AllPeriodsView

    def test_title(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate', relatedstudent__user=requestuser)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertIn(
                'Your courses',
                mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate', relatedstudent__user=requestuser)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
                'Your courses',
                mockresponse.selector.one('h1').alltext_normalized)

    def __get_period_count(self, selector):
        return selector.count('.django-cradmin-listbuilder-itemvalue')

    def test_not_periods_where_not_student(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
                0,
                self.__get_period_count(selector=mockresponse.selector))

    def test_not_future_periods(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.RelatedStudent',
                   user=requestuser,
                   period=mommy.make_recipe('devilry.apps.core.period_future'))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
                0,
                self.__get_period_count(selector=mockresponse.selector))

    def test_include_old_periods(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.RelatedStudent',
                   user=requestuser,
                   period=mommy.make_recipe('devilry.apps.core.period_old'))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
                1,
                self.__get_period_count(selector=mockresponse.selector))

    def test_include_active_periods(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.RelatedStudent', user=requestuser,
                   period=mommy.make_recipe('devilry.apps.core.period_active'))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
                1,
                self.__get_period_count(selector=mockresponse.selector))

    def test_no_items_message(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
                'You are not registered on any courses in Devilry.',
                mockresponse.selector.one('.django-cradmin-listing-no-items-message').alltext_normalized)

    def __get_titles(self, selector):
        return [element.alltext_normalized
                for element in selector.list('.django-cradmin-listbuilder-itemvalue-titledescription-title')]

    def test_orderby_sanity(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod1 = mommy.make_recipe('devilry.apps.core.period_old',
                                        parentnode__long_name='Test Subject',
                                        long_name='Old Period 1')
        testperiod2 = mommy.make_recipe('devilry.apps.core.period_old',
                                        parentnode__long_name='Test Subject',
                                        start_time=OLD_PERIOD_START + timedelta(days=2),
                                        long_name='Old Period 2')
        testperiod3 = mommy.make_recipe('devilry.apps.core.period_active',
                                        parentnode__long_name='Test Subject',
                                        start_time=ACTIVE_PERIOD_START + timedelta(days=2),
                                        long_name='Active Period 2')
        testperiod4 = mommy.make_recipe('devilry.apps.core.period_active',
                                        parentnode__long_name='Test Subject',
                                        long_name='Active Period 1')
        mommy.make('core.RelatedStudent', period=testperiod1, user=requestuser)
        mommy.make('core.RelatedStudent', period=testperiod2, user=requestuser)
        mommy.make('core.RelatedStudent', period=testperiod3, user=requestuser)
        mommy.make('core.RelatedStudent', period=testperiod4, user=requestuser)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=requestuser)
        self.assertEqual(
                [
                    'Test Subject - Active Period 2',
                    'Test Subject - Active Period 1',
                    'Test Subject - Old Period 2',
                    'Test Subject - Old Period 1',
                ],
                self.__get_titles(mockresponse.selector))

    def test_orderby_multiple_with_same_start_time(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod1 = mommy.make_recipe('devilry.apps.core.period_active',
                                        parentnode__long_name='Test Subject 1',
                                        long_name='Active Period')
        testperiod2 = mommy.make_recipe('devilry.apps.core.period_active',
                                        parentnode__long_name='Test Subject 2',
                                        long_name='Active Period')
        testperiod3 = mommy.make_recipe('devilry.apps.core.period_active',
                                        parentnode__long_name='Test Subject 3',
                                        long_name='Active Period')
        mommy.make('core.RelatedStudent', period=testperiod1, user=requestuser)
        mommy.make('core.RelatedStudent', period=testperiod2, user=requestuser)
        mommy.make('core.RelatedStudent', period=testperiod3, user=requestuser)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=requestuser)
        self.assertEqual(
                [
                    'Test Subject 1 - Active Period',
                    'Test Subject 2 - Active Period',
                    'Test Subject 3 - Active Period',
                ],
                self.__get_titles(mockresponse.selector))

    def test_listitem_title_sanity(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make_recipe('devilry.apps.core.period_active',
                                       parentnode__long_name='Test Subject',
                                       long_name='Test Period')
        mommy.make('core.RelatedStudent', period=testperiod, user=requestuser)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
            'Test Subject - Test Period',
            mockresponse.selector.one(
                    '.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized
        )

    def test_listitem_url(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        mommy.make('core.RelatedStudent', period=testperiod, user=requestuser)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
                '#',
                # reverse_cradmin_url(
                #         instanceid='devilry_student_period',
                #         appname='overview',
                #         roleid=testperiod.id,
                #         viewname=crapp.INDEXVIEW_NAME,
                # ),
                mockresponse.selector.one('a.devilry-student-listbuilder-period-itemframe')['href'])

    # def test_qualifies_for_final_exam_qualified(self):
    #     periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
    #         .add_relatedstudents(self.requestuser)
    #     status = Status.objects.create(period=periodbuilder.period,
    #                                    user=UserBuilder('testadmin').user,
    #                                    status=Status.READY)
    #     status.students.create(
    #         relatedstudent=periodbuilder.period.relatedstudent_set.get(user=self.requestuser),
    #         qualifies=True)
    #
    #     response = self._get_as('requestuser')
    #     self.assertEquals(response.status_code, 200)
    #     selector = htmls.S(response.content)
    #     self.assertTrue(
    #         selector.exists('#objecttableview-table tbody tr td:nth-child(1) '
    #                         '.devilry-student-allperiodsapp-qualified-for-final-exam-wrapper'))
    #     self.assertEquals(
    #         selector.one('#objecttableview-table tbody tr td:nth-child(1) '
    #                      '.devilry-student-allperiodsapp-qualified-for-final-exam').alltext_normalized,
    #         'Qualified for final exam')
    #     self.assertTrue(
    #         selector.exists('#objecttableview-table tbody tr td:nth-child(1) .label-success'))
    #
    # def test_qualifies_for_final_exam_not_qualified(self):
    #     periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
    #         .add_relatedstudents(self.requestuser)
    #     status = Status.objects.create(period=periodbuilder.period,
    #                                    user=UserBuilder('testadmin').user,
    #                                    status=Status.READY)
    #     status.students.create(
    #         relatedstudent=periodbuilder.period.relatedstudent_set.get(user=self.requestuser),
    #         qualifies=False)
    #
    #     response = self._get_as('requestuser')
    #     self.assertEquals(response.status_code, 200)
    #     selector = htmls.S(response.content)
    #     self.assertTrue(
    #         selector.exists('#objecttableview-table tbody tr td:nth-child(1) '
    #                         '.devilry-student-allperiodsapp-qualified-for-final-exam-wrapper'))
    #     self.assertEquals(
    #         selector.one('#objecttableview-table tbody tr td:nth-child(1) '
    #                      '.devilry-student-allperiodsapp-not-qualified-for-final-exam').alltext_normalized,
    #         'Not qualified for final exam')
    #     self.assertTrue(
    #         selector.exists('#objecttableview-table tbody tr td:nth-child(1) .label-warning'))
    #
    # def test_qualifies_for_final_exam_not_set(self):
    #     PeriodBuilder.quickadd_ducku_duck1010_active()\
    #         .add_relatedstudents(self.requestuser)
    #     response = self._get_as('requestuser')
    #     self.assertEquals(response.status_code, 200)
    #     selector = htmls.S(response.content)
    #     self.assertFalse(
    #         selector.exists('#objecttableview-table tbody tr td:nth-child(1) '
    #                         '.devilry-student-allperiodsapp-qualified-for-final-exam-wrapper'))
    #
    # def test_is_active(self):
    #     PeriodBuilder.quickadd_ducku_duck1010_active()\
    #         .add_relatedstudents(self.requestuser)
    #     response = self._get_as('requestuser')
    #     self.assertEquals(response.status_code, 200)
    #     selector = htmls.S(response.content)
    #     self.assertTrue(
    #         selector.exists('#objecttableview-table tbody tr td:nth-child(1) '
    #                         'strong.devilry-student-allperiodsapp-isactive'))
    #
    # def test_is_not_active(self):
    #     SubjectBuilder.quickadd_ducku_duck1010()\
    #         .add_6month_lastyear_period()\
    #         .add_relatedstudents(self.requestuser)
    #     response = self._get_as('requestuser')
    #     self.assertEquals(response.status_code, 200)
    #     selector = htmls.S(response.content)
    #     self.assertFalse(
    #         selector.exists('#objecttableview-table tbody tr td:nth-child(1) '
    #                         'strong.devilry-student-allperiodsapp-isactive'))
