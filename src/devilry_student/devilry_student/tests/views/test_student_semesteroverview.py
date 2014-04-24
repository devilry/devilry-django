from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.models import GroupInvite
from devilry_developer.testhelpers.soupselect import cssFind
from devilry_developer.testhelpers.soupselect import cssGet
from devilry_developer.testhelpers.soupselect import prettyhtml
from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.corebuilder import NodeBuilder
from devilry_developer.testhelpers.corebuilder import SubjectBuilder
from devilry_qualifiesforexam.models import Status

class TestSemesterOverview(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user

    def _getas(self, user, *args, **kwargs):
        self.client.login(username=user.username, password='test')
        url = reverse('devilry_student_browseperiod', args=[kwargs['id']])
        return self.client.get(url, *args, **kwargs)

    def _postas(self, user, *args, **kwargs):
        self.client.login(username=user.username, password='test')
        return self.client.post(url, *args, **kwargs)

    # def test_not_logged_in(self):
    #     response = self.client.get(self.url)
    #     self.assertRedirects(response, expected_url='http://testserver/authenticate/login?next=/devilry_student/browse/', 
    #         status_code=302, target_status_code=200)

    # def test_render_header(self):
    #     response = self._getas(self.testuser)
    #     html = response.content
    #     self.assertEquals(cssGet(html, '.page-header h1').text.strip(), "Browse")
    #     #self.assertEquals(cssGet(html, '.page-header .subheader').text.strip(), "Browse all your courses")

    # def test_period_list(self):
    #     node = SubjectBuilder.quickadd_ducku_duck1010()
    #     period1 = node.add_6month_active_period()
    #     period2 = node.add_6month_lastyear_period()

    #     student1 = UserBuilder('student1').user

    #     period1.add_relatedstudents(self.testuser, student1)
    #     period2.add_relatedstudents(self.testuser)

    #     response = self._getas(self.testuser)
    #     html = response.content
    #     self.assertEquals(len(cssFind(html, '.period-list-element')), 2)

    #     response = self._getas(student1)
    #     html = response.content
    #     self.assertEquals(len(cssFind(html, '.period-list-element')), 1)

    def test_get_qualifiesforexam_false(self):
        period = PeriodBuilder.quickadd_ducku_duck1010_active()
        
        groupbuilder = period.add_assignment('assignment1')\
        .add_group(students=[self.testuser])
        period.add_relatedstudents(self.testuser)

        deadline1builder = groupbuilder.add_deadline_x_weeks_ago(weeks=4)
        delivery1 = deadline1builder.add_delivery_x_hours_before_deadline(hours=10).delivery

        relatedstudent = period.period.relatedstudent_set.get(user=self.testuser)

        status = Status.objects.create(period=period.period,
                user=self.testuser,
                status=Status.READY)
        status.students.create(relatedstudent=relatedstudent, qualifies=False)

        response = self._getas(self.testuser, id=period.period.id)
        html = response.content
        self.assertEquals(response.status_code, 200)

        self.assertEquals(len(cssFind(html, '.qualifies-for-exams')), 0)

    def test_get_qualifiesforexam_true(self):
        period = PeriodBuilder.quickadd_ducku_duck1010_active()
        
        groupbuilder = period.add_assignment('assignment1')\
        .add_group(students=[self.testuser])
        period.add_relatedstudents(self.testuser)

        deadline1builder = groupbuilder.add_deadline_x_weeks_ago(weeks=4)
        delivery1 = deadline1builder.add_delivery_x_hours_before_deadline(hours=10).delivery

        relatedstudent = period.period.relatedstudent_set.get(user=self.testuser)

        status = Status.objects.create(period=period.period,
                user=self.testuser,
                status=Status.READY)
        status.students.create(relatedstudent=relatedstudent, qualifies=True)

        response = self._getas(self.testuser, id=period.period.id)
        html = response.content
        self.assertEquals(response.status_code, 200)

        self.assertEquals(len(cssFind(html, '.qualifies-for-exams')), 1)
        
    # def test_get_qualifiesforexam_none(self):
    #     self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1).d1')
    #     content, response = self._getas('student1')
    #     subjects = content
    #     self.assertEquals(response.status_code, 200)
    #     period = subjects[0]['periods'][0]
    #     self.assertIsNone(period['qualifiesforexams'])

    # def test_get_qualifiesforexam_notready(self):
    #     self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1).d1')
    #     status = Status.objects.create(period=self.testhelper.sub_p1,
    #             user=self.testhelper.testuser,
    #             status=Status.NOTREADY)
    #     relstudent = self.testhelper.sub_p1.relatedstudent_set.create(user=self.testhelper.student1)
    #     status.students.create(relatedstudent=relstudent, qualifies=False)

    #     content, response = self._getas('student1')
    #     subjects = content
    #     self.assertEquals(response.status_code, 200)
    #     period = subjects[0]['periods'][0]
    #     self.assertIsNone(period['qualifiesforexams'])
