

from datetime import timedelta

from django import test
from django.conf import settings
from cradmin_legacy import cradmin_testhelpers
from cradmin_legacy.crinstance import reverse_cradmin_url
from cradmin_legacy import crapp
from model_bakery import baker

from devilry.apps.core.baker_recipes import OLD_PERIOD_START, ACTIVE_PERIOD_START, ACTIVE_PERIOD_END
from devilry.devilry_qualifiesforexam.models import Status
from devilry.devilry_student.views.dashboard import allperiods


class TestAllPeriodsView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = allperiods.AllPeriodsView

    def test_title(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Candidate', relatedstudent__user=requestuser)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertIn(
                'Your courses',
                mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Candidate', relatedstudent__user=requestuser)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
                'Your courses',
                mockresponse.selector.one('h1').alltext_normalized)

    def __get_period_count(self, selector):
        return selector.count('.cradmin-legacy-listbuilder-itemvalue')

    def test_not_periods_where_not_student(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
                0,
                self.__get_period_count(selector=mockresponse.selector))

    def test_not_future_periods(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.RelatedStudent',
                   user=requestuser,
                   period=baker.make_recipe('devilry.apps.core.period_future'))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
                0,
                self.__get_period_count(selector=mockresponse.selector))

    def test_include_old_periods(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.RelatedStudent',
                   user=requestuser,
                   period=baker.make_recipe('devilry.apps.core.period_old'))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
                1,
                self.__get_period_count(selector=mockresponse.selector))

    def test_include_active_periods(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.RelatedStudent', user=requestuser,
                   period=baker.make_recipe('devilry.apps.core.period_active'))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
                1,
                self.__get_period_count(selector=mockresponse.selector))

    def test_no_items_message(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
                'You are not registered on any courses in Devilry.',
                mockresponse.selector.one('.cradmin-legacy-listing-no-items-message').alltext_normalized)

    def __get_titles(self, selector):
        return [element.alltext_normalized
                for element in selector.list('.cradmin-legacy-listbuilder-itemvalue-titledescription-title')]

    def test_orderby_sanity(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod1 = baker.make_recipe('devilry.apps.core.period_old',
                                        parentnode__long_name='Test Subject',
                                        long_name='Old Period 1')
        testperiod2 = baker.make_recipe('devilry.apps.core.period_old',
                                        parentnode__long_name='Test Subject',
                                        start_time=OLD_PERIOD_START + timedelta(days=2),
                                        long_name='Old Period 2')
        testperiod3 = baker.make_recipe('devilry.apps.core.period_active',
                                        parentnode__long_name='Test Subject',
                                        start_time=ACTIVE_PERIOD_START + timedelta(days=2),
                                        long_name='Active Period 2')
        testperiod4 = baker.make_recipe('devilry.apps.core.period_active',
                                        parentnode__long_name='Test Subject',
                                        long_name='Active Period 1')
        baker.make('core.RelatedStudent', period=testperiod1, user=requestuser)
        baker.make('core.RelatedStudent', period=testperiod2, user=requestuser)
        baker.make('core.RelatedStudent', period=testperiod3, user=requestuser)
        baker.make('core.RelatedStudent', period=testperiod4, user=requestuser)
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
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod1 = baker.make_recipe('devilry.apps.core.period_active',
                                        parentnode__long_name='Test Subject 1',
                                        long_name='Active Period')
        testperiod2 = baker.make_recipe('devilry.apps.core.period_active',
                                        parentnode__long_name='Test Subject 2',
                                        long_name='Active Period')
        testperiod3 = baker.make_recipe('devilry.apps.core.period_active',
                                        parentnode__long_name='Test Subject 3',
                                        long_name='Active Period')
        baker.make('core.RelatedStudent', period=testperiod1, user=requestuser)
        baker.make('core.RelatedStudent', period=testperiod2, user=requestuser)
        baker.make('core.RelatedStudent', period=testperiod3, user=requestuser)
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
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active',
                                       parentnode__long_name='Test Subject',
                                       long_name='Test Period')
        baker.make('core.RelatedStudent', period=testperiod, user=requestuser)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
            'Test Subject - Test Period',
            mockresponse.selector.one(
                    '.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized
        )

    def test_listitem_url(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        baker.make('core.RelatedStudent', period=testperiod, user=requestuser)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
                reverse_cradmin_url(
                        instanceid='devilry_student_period',
                        appname='overview',
                        roleid=testperiod.id,
                        viewname=crapp.INDEXVIEW_NAME,
                ),
                mockresponse.selector.one('a.devilry-student-listbuilder-period-itemframe')['href'])

    def test_assignmentcount_sanity(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        relatedstudent = baker.make('core.RelatedStudent', user=requestuser, period=testperiod)
        testassignment1 = baker.make('core.Assignment', parentnode=testperiod)
        baker.make('core.Candidate',
                   assignment_group__parentnode=testassignment1,
                   relatedstudent=relatedstudent)
        testassignment2 = baker.make('core.Assignment', parentnode=testperiod)
        baker.make('core.Candidate',
                   assignment_group__parentnode=testassignment2,
                   relatedstudent=relatedstudent)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertEqual(
                '2 assignments',
                mockresponse.selector.one(
                        '.cradmin-legacy-listbuilder-itemvalue-titledescription-description').alltext_normalized)

    def test_assignmentcount_multiple_periods(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod1 = baker.make_recipe('devilry.apps.core.period_active')
        relatedstudent1 = baker.make('core.RelatedStudent', user=requestuser, period=testperiod1)
        testassignment1 = baker.make('core.Assignment', parentnode=testperiod1)
        baker.make('core.Candidate',
                   assignment_group__parentnode=testassignment1,
                   relatedstudent=relatedstudent1)

        testperiod2 = baker.make_recipe('devilry.apps.core.period_active')
        baker.make('core.RelatedStudent', user=requestuser, period=testperiod2)

        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        assignmentcounts = {
            element.alltext_normalized
            for element in mockresponse.selector.list(
                    '.cradmin-legacy-listbuilder-itemvalue-titledescription-description')}
        self.assertEqual(
                {'1 assignment', '0 assignments'},
                assignmentcounts)

    def test_qualified_for_final_exam_sanity_no_status(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        baker.make('core.RelatedStudent', period=testperiod, user=requestuser)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertFalse(mockresponse.selector.exists('.devilry-cradmin-perioditemvalue-student-qualifedforexam'))

    def test_qualified_for_final_exam_sanity_qualified(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=requestuser)
        status = baker.make('devilry_qualifiesforexam.Status', period=testperiod,
                            status=Status.READY)
        baker.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=relatedstudent,
                   status=status,
                   qualifies=True)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertTrue(mockresponse.selector.exists(
                '.devilry-cradmin-perioditemvalue-student-qualifedforexam'
                '.devilry-cradmin-perioditemvalue-student-qualifedforexam-yes'))

    def test_qualified_for_final_exam_sanity_not_qualified(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod, user=requestuser)
        status = baker.make('devilry_qualifiesforexam.Status', period=testperiod,
                            status=Status.READY)
        baker.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   relatedstudent=relatedstudent,
                   status=status,
                   qualifies=False)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertTrue(mockresponse.selector.exists(
                '.devilry-cradmin-perioditemvalue-student-qualifedforexam'
                '.devilry-cradmin-perioditemvalue-student-qualifedforexam-no'))

    def test_no_pagination(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.RelatedStudent',
                   period__start_time=ACTIVE_PERIOD_START,
                   period__end_time=ACTIVE_PERIOD_END,
                   user=requestuser,
                   _quantity=allperiods.AllPeriodsView.paginate_by)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertFalse(mockresponse.selector.exists('.cradmin-legacy-loadmorepager'))

    def test_pagination(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.RelatedStudent',
                   period__start_time=ACTIVE_PERIOD_START,
                   period__end_time=ACTIVE_PERIOD_END,
                   user=requestuser,
                   _quantity=allperiods.AllPeriodsView.paginate_by + 1)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=requestuser)
        self.assertTrue(mockresponse.selector.exists('.cradmin-legacy-loadmorepager'))

    def test_querycount(self):
        requestuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.RelatedStudent',
                   period__start_time=ACTIVE_PERIOD_START,
                   period__end_time=ACTIVE_PERIOD_END,
                   user=requestuser,
                   _quantity=10)
        with self.assertNumQueries(2):
            self.mock_http200_getrequest_htmls(requestuser=requestuser)
