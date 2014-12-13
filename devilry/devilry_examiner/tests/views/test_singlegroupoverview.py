from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.project.develop.testhelpers.corebuilder import SubjectBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.project.develop.testhelpers.soupselect import cssFind
from devilry.project.develop.testhelpers.soupselect import cssGet
from devilry.project.develop.testhelpers.soupselect import cssExists
from devilry.project.develop.testhelpers.soupselect import normalize_whitespace
# from develop.testhelpers.soupselect import prettyhtml



_DJANGO_ISODATETIMEFORMAT = 'Y-m-d H:i'

def _isoformat_datetime(datetimeobj):
    return datetimeobj.strftime('%Y-%m-%d %H:%M')


class TestSingleGroupOverview(TestCase):
    def setUp(self):
        self.examiner1 = UserBuilder('examiner1').user
        self.student1 = UserBuilder('student1', full_name="Student One").user
        self.duck1010builder = SubjectBuilder.quickadd_ducku_duck1010()
        self.week1builder = self.duck1010builder.add_6month_active_period()\
            .add_assignment('week1', long_name='Week 1')

    def _getas(self, username, groupid, *args, **kwargs):
        self.client.login(username=username, password='test')
        return self.client.get(reverse('devilry_examiner_singlegroupoverview', kwargs={'groupid': groupid}),
                *args, **kwargs)

    def test_404_when_not_examiner(self):
        groupbuilder = self.week1builder.add_group(
            students=[self.student1])
        response = self._getas('examiner1', groupbuilder.group.id)
        self.assertEquals(response.status_code, 404)

    def test_404_when_inactive(self):
        groupbuilder = self.duck1010builder.add_6month_nextyear_period()\
            .add_assignment('week1')\
            .add_group(examiners=[self.examiner1])
        response = self._getas('examiner1', groupbuilder.group.id)
        self.assertEquals(response.status_code, 404)

    def test_header(self):
        groupbuilder = self.week1builder.add_group(
            students=[self.student1],
            examiners=[self.examiner1])
        response = self._getas('examiner1', groupbuilder.group.id)
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertEquals(cssGet(html, '.page-header h1').text.strip(),
            'Week 1 &mdash; Student One')
        self.assertEquals(cssGet(html, '.page-header .subheader').text.strip(),
            'duck1010, active')

    def test_deadline_render(self):
        groupbuilder = self.week1builder.add_group(
                examiners=[self.examiner1])
        deadlinebuilder = groupbuilder.add_deadline_in_x_weeks(weeks=1, text='This is the deadline text.')
        with self.settings(DATETIME_FORMAT=_DJANGO_ISODATETIMEFORMAT, USE_L10N=False):
            response = self._getas('examiner1', groupbuilder.group.id)
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertEquals(cssGet(html, '.deadlinebox h2 .deadline-header-prefix').text.strip(),
            'Deadline 1')
        self.assertEquals(cssGet(html, '.deadlinebox h2 .deadline-datetime').text.strip(),
            _isoformat_datetime(deadlinebuilder.deadline.deadline))
        self.assertEquals(cssGet(html, '.deadlinebox .deadline-text').text.strip(),
            'This is the deadline text.')

    def test_deadline_render_no_text(self):
        groupbuilder = self.week1builder.add_group(
                examiners=[self.examiner1])
        deadlinebuilder = groupbuilder.add_deadline_in_x_weeks(weeks=1)
        response = self._getas('examiner1', groupbuilder.group.id)
        html = response.content
        self.assertEquals(len(cssFind(html, '.deadlinebox .deadline-text')), 0)

    def test_deadline_ordering(self):
        groupbuilder = self.week1builder.add_group(
                examiners=[self.examiner1])
        deadline2 = groupbuilder.add_deadline_in_x_weeks(weeks=1).deadline
        deadline3 = groupbuilder.add_deadline_in_x_weeks(weeks=2).deadline
        deadline1 = groupbuilder.add_deadline_x_weeks_ago(weeks=1).deadline
        with self.settings(DATETIME_FORMAT=_DJANGO_ISODATETIMEFORMAT, USE_L10N=False):
            response = self._getas('examiner1', groupbuilder.group.id)
        self.assertEquals(response.status_code, 200)
        html = response.content
        prefixes = map(lambda element: element.text.strip(), cssFind(html, '.deadline-header-prefix'))
        self.assertEquals(prefixes, ['Deadline 3', 'Deadline 2', 'Deadline 1'])
        datetimes = map(lambda element: element.text.strip(), cssFind(html, '.deadline-datetime'))
        self.assertEquals(datetimes,
            [_isoformat_datetime(deadline.deadline) for deadline in (deadline3, deadline2, deadline1)])

    def test_no_deliveries_on_deadline(self):
        groupbuilder = self.week1builder.add_group(
                examiners=[self.examiner1])
        deadlinebuilder = groupbuilder.add_deadline_in_x_weeks(weeks=1)
        response = self._getas('examiner1', groupbuilder.group.id)
        html = response.content
        self.assertEquals(cssGet(html, '.deadlinebox .no-deliveries-message').text.strip(),
            'No deliveries')

    def test_delivery_render(self):
        groupbuilder = self.week1builder.add_group(
                examiners=[self.examiner1])
        delivery = groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery().delivery
        with self.settings(DATETIME_FORMAT=_DJANGO_ISODATETIMEFORMAT, USE_L10N=False):
            response = self._getas('examiner1', groupbuilder.group.id)
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertEquals(cssGet(html, '.delivery h3 a').text.strip(), 'Delivery #1')
        self.assertEquals(cssGet(html, '.delivery .no-feedback-message').text.strip(), 'No feedback')
        self.assertEquals(cssGet(html, '.delivery .time_of_delivery').text.strip(),
            _isoformat_datetime(delivery.time_of_delivery))
        self.assertFalse(cssExists(html, '.delivery .after_deadline_message'))

    def test_delivery_render_passed_grade(self):
        groupbuilder = self.week1builder.add_group(
                examiners=[self.examiner1])
        delivery = groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()\
            .add_feedback(
                grade='10/20',
                points=10,
                is_passing_grade=True,
                saved_by=self.examiner1)
        response = self._getas('examiner1', groupbuilder.group.id)
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertEquals(cssGet(html, '.delivery .last-feedback .feedback-grade').text.strip(),
            '10/20')
        self.assertEquals(cssGet(html, '.delivery .last-feedback .feedback-is_passing_grade').text.strip(),
            'passed')
        self.assertIn('text-success', cssGet(html, '.delivery .last-feedback')['class'])

    def test_delivery_render_failed_grade(self):
        groupbuilder = self.week1builder.add_group(
                examiners=[self.examiner1])
        delivery = groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery()\
            .add_feedback(
                grade='2/20',
                points=2,
                is_passing_grade=False,
                saved_by=self.examiner1)
        response = self._getas('examiner1', groupbuilder.group.id)
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertEquals(cssGet(html, '.delivery .last-feedback .feedback-grade').text.strip(),
            '2/20')
        self.assertEquals(cssGet(html, '.delivery .last-feedback .feedback-is_passing_grade').text.strip(),
            'failed')
        self.assertIn('text-warning', cssGet(html, '.delivery .last-feedback')['class'])

    def test_delivery_render_after_deadline(self):
        groupbuilder = self.week1builder.add_group(
                examiners=[self.examiner1])
        delivery = groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_after_deadline(hours=2).delivery
        response = self._getas('examiner1', groupbuilder.group.id)
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertEquals(
            normalize_whitespace(cssGet(html, '.delivery .after_deadline_message').text),
            "2 hours after the deadline")

    def test_delivery_order(self):
        groupbuilder = self.week1builder.add_group(
                examiners=[self.examiner1])
        deadlinebuilder = groupbuilder.add_deadline_in_x_weeks(weeks=1)
        delivery1 = deadlinebuilder.add_delivery_x_hours_before_deadline(hours=10).delivery
        delivery2 = deadlinebuilder.add_delivery_x_hours_before_deadline(hours=5).delivery
        delivery3 = deadlinebuilder.add_delivery_x_hours_before_deadline(hours=1).delivery
        with self.settings(DATETIME_FORMAT=_DJANGO_ISODATETIMEFORMAT, USE_L10N=False):
            response = self._getas('examiner1', groupbuilder.group.id)
        html = response.content
        deliveries = map(lambda element: element.text.strip(), cssFind(html, '.delivery h3 a'))
        self.assertEquals(deliveries,
            ['Delivery #3', 'Delivery #2', 'Delivery #1'])
        datetimes = map(lambda element: element.text.strip(), cssFind(html, '.delivery .time_of_delivery'))
        self.assertEquals(datetimes, [
            _isoformat_datetime(delivery3.time_of_delivery),
            _isoformat_datetime(delivery2.time_of_delivery),
            _isoformat_datetime(delivery1.time_of_delivery),
        ])

    def test_give_another_chance(self):
        groupbuilder = self.week1builder\
            .add_group(students=[self.student1], examiners=[self.examiner1])
        deliverybuilder = groupbuilder\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        deliverybuilder.add_failed_feedback(saved_by=UserBuilder('testuser').user)
        response = self._getas('examiner1', groupbuilder.group.id)
        html = response.content

        groupbuilder.reload_from_db()
        self.assertEquals(groupbuilder.group.feedback, deliverybuilder.delivery.last_feedback)
        self.assertEquals(groupbuilder.group.delivery_status, 'corrected')
        self.assertFalse(groupbuilder.group.feedback.is_passing_grade)
        self.assertTrue(cssExists(html, '.devilry_give_another_chance_box'))
        box = cssGet(html, '.devilry_give_another_chance_box')
        self.assertIn('The last feedback for this group is a failing grade.', box.text.strip())
        self.assertEquals(cssGet(html, '.devilry_give_another_chance_box form input[name=group_ids]')['value'],
            str(groupbuilder.group.id))
        self.assertEquals(cssGet(html, '.devilry_give_another_chance_box form input[name=give_another_chance]')['value'],
            'true')
        self.assertEquals(cssGet(html, '.devilry_give_another_chance_box form input[name=success_url]')['value'],
            reverse('devilry_examiner_singlegroupoverview', kwargs={'groupid': groupbuilder.group.id}))
        self.assertEquals(cssGet(html, '.devilry_give_another_chance_box form input[name=cancel_url]')['value'],
            reverse('devilry_examiner_singlegroupoverview', kwargs={'groupid': groupbuilder.group.id}))

    def test_give_another_chance_only_when_failed(self):
        groupbuilder = self.week1builder\
            .add_group(students=[self.student1], examiners=[self.examiner1])
        deliverybuilder = groupbuilder\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        deliverybuilder.add_passed_feedback(saved_by=UserBuilder('testuser').user)
        response = self._getas('examiner1', groupbuilder.group.id)
        html = response.content
        groupbuilder.reload_from_db()
        self.assertEquals(groupbuilder.group.feedback, deliverybuilder.delivery.last_feedback)
        self.assertEquals(groupbuilder.group.delivery_status, 'corrected')
        self.assertTrue(groupbuilder.group.feedback.is_passing_grade)
        self.assertFalse(cssExists(html, '.devilry_give_another_chance_box'))

    def test_add_deadline_anytime_form(self):
        groupbuilder = self.week1builder.add_group(examiners=[self.examiner1])
        groupbuilder.add_deadline_in_x_weeks(weeks=1)
        html = self._getas('examiner1', groupbuilder.group.id).content
        self.assertTrue(cssExists(html, '.devilry_add_deadline_anytime_form'))
        self.assertFalse(cssExists(html, '.devilry_give_another_chance_box'))

    def test_missing_expected_delivery_box(self):
        groupbuilder = self.week1builder.add_group(examiners=[self.examiner1])
        groupbuilder.add_deadline_x_weeks_ago(weeks=1)
        html = self._getas('examiner1', groupbuilder.group.id).content
        self.assertTrue(cssExists(html, '.devilry_missing_expected_delivery_box'))

    def test_add_nonelectronic_delivery_anytime_form(self):
        groupbuilder = self.week1builder.add_group(examiners=[self.examiner1])
        groupbuilder.add_deadline_in_x_weeks(weeks=1)
        html = self._getas('examiner1', groupbuilder.group.id).content
        self.assertTrue(cssExists(html, '.devilry_add_nonelectronic_delivery_anytime_form'))
        self.assertFalse(cssExists(html, '.devilry_missing_expected_delivery_box'))
