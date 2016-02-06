from django import test
from django.conf import settings
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.devilry_student.views.dashboard import allperiods


class TestAllPeriodsView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = allperiods.AllPeriodsView

    def test_title(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate', relatedstudent__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertIn(
                'Your courses',
                mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate', relatedstudent__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                'Your courses',
                mockresponse.selector.one('h1').alltext_normalized)

    def __get_period_count(self, selector):
        return selector.count('.django-cradmin-listbuilder-itemvalue')

    def test_not_periods_where_not_student(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                0,
                self.__get_period_count(selector=mockresponse.selector))

    def test_not_future_periods(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.RelatedStudent',
                   user=testuser,
                   period=mommy.make_recipe('devilry.apps.core.period_future'))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                0,
                self.__get_period_count(selector=mockresponse.selector))

    def test_include_old_periods(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.RelatedStudent',
                   user=testuser,
                   period=mommy.make_recipe('devilry.apps.core.period_old'))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                1,
                self.__get_period_count(selector=mockresponse.selector))

    def test_include_active_periods(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.RelatedStudent', user=testuser,
                   period=mommy.make_recipe('devilry.apps.core.period_active'))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                1,
                self.__get_period_count(selector=mockresponse.selector))

    # def test_qualifies_for_final_exam_qualified(self):
    #     periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
    #         .add_relatedstudents(self.testuser)
    #     status = Status.objects.create(period=periodbuilder.period,
    #                                    user=UserBuilder('testadmin').user,
    #                                    status=Status.READY)
    #     status.students.create(
    #         relatedstudent=periodbuilder.period.relatedstudent_set.get(user=self.testuser),
    #         qualifies=True)
    #
    #     response = self._get_as('testuser')
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
    #         .add_relatedstudents(self.testuser)
    #     status = Status.objects.create(period=periodbuilder.period,
    #                                    user=UserBuilder('testadmin').user,
    #                                    status=Status.READY)
    #     status.students.create(
    #         relatedstudent=periodbuilder.period.relatedstudent_set.get(user=self.testuser),
    #         qualifies=False)
    #
    #     response = self._get_as('testuser')
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
    #         .add_relatedstudents(self.testuser)
    #     response = self._get_as('testuser')
    #     self.assertEquals(response.status_code, 200)
    #     selector = htmls.S(response.content)
    #     self.assertFalse(
    #         selector.exists('#objecttableview-table tbody tr td:nth-child(1) '
    #                         '.devilry-student-allperiodsapp-qualified-for-final-exam-wrapper'))
    #
    # def test_is_active(self):
    #     PeriodBuilder.quickadd_ducku_duck1010_active()\
    #         .add_relatedstudents(self.testuser)
    #     response = self._get_as('testuser')
    #     self.assertEquals(response.status_code, 200)
    #     selector = htmls.S(response.content)
    #     self.assertTrue(
    #         selector.exists('#objecttableview-table tbody tr td:nth-child(1) '
    #                         'strong.devilry-student-allperiodsapp-isactive'))
    #
    # def test_is_not_active(self):
    #     SubjectBuilder.quickadd_ducku_duck1010()\
    #         .add_6month_lastyear_period()\
    #         .add_relatedstudents(self.testuser)
    #     response = self._get_as('testuser')
    #     self.assertEquals(response.status_code, 200)
    #     selector = htmls.S(response.content)
    #     self.assertFalse(
    #         selector.exists('#objecttableview-table tbody tr td:nth-child(1) '
    #                         'strong.devilry-student-allperiodsapp-isactive'))
