from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.testhelper import TestHelper
from devilry_developer.testhelpers.corebuilder import SubjectBuilder
from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.soupselect import cssFind
from devilry_developer.testhelpers.soupselect import cssGet
from devilry_developer.testhelpers.soupselect import cssExists



_DJANGO_ISODATETIMEFORMAT = 'Y-m-d H:i'

def _isoformat_datetime(datetimeobj):
    return datetimeobj.strftime('%Y-%m-%d %H:%M')


class TestSingleDeliveryView(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.examiner1 = UserBuilder('examiner1').user
        self.student1 = UserBuilder('student1', full_name="Student One").user
        self.duck1010builder = SubjectBuilder.quickadd_ducku_duck1010()
        self.week1builder = self.duck1010builder.add_6month_active_period()\
            .add_assignment('week1', long_name='Week 1')

    def _getas(self, username, deliveryid, *args, **kwargs):
        self.client.login(username=username, password='test')
        return self.client.get(reverse('devilry_examiner_singledeliveryview', kwargs={'deliveryid': deliveryid}),
                *args, **kwargs)

    def test_404_when_not_examiner(self):
        deliverybuilder = self.week1builder\
            .add_group(students=[self.student1])\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        response = self._getas('examiner1', deliverybuilder.delivery.id)
        self.assertEquals(response.status_code, 404)

    def test_404_when_inactive(self):
        deliverybuilder = self.duck1010builder.add_6month_nextyear_period()\
            .add_assignment('week1')\
            .add_group(examiners=[self.examiner1])\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        response = self._getas('examiner1', deliverybuilder.delivery.id)
        self.assertEquals(response.status_code, 404)

    def test_header(self):
        deliverybuilder = self.week1builder\
            .add_group(students=[self.student1], examiners=[self.examiner1])\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        with self.settings(DATETIME_FORMAT=_DJANGO_ISODATETIMEFORMAT, USE_L10N=False):
            response = self._getas('examiner1', deliverybuilder.delivery.id)
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertEquals(cssGet(html, '.page-header h1').text.strip(),
            'Week 1 &mdash; Student One')
        self.assertEquals(cssGet(html, '.page-header .subheader').text.strip(),
            'Delivery 1/1, {}'.format(_isoformat_datetime(deliverybuilder.delivery.time_of_delivery)))