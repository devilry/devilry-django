from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.models import GroupInvite
from devilry.project.develop.testhelpers.soupselect import cssFind
from devilry.project.develop.testhelpers.soupselect import cssGet
from devilry.project.develop.testhelpers.soupselect import prettyhtml
from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.project.develop.testhelpers.corebuilder import NodeBuilder
from devilry.project.develop.testhelpers.corebuilder import SubjectBuilder
from devilry_qualifiesforexam.models import Status

class TestSemesterOverview(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user

    def _get_url(self, id):
        return reverse('devilry_student_browseperiod', args=[id])        

    def _getas(self, user, *args, **kwargs):
        self.client.login(username=user.username, password='test')
        url = reverse('devilry_student_browseperiod', args=[kwargs['id']])
        return self.client.get(url, *args, **kwargs)

    def _postas(self, user, *args, **kwargs):
        self.client.login(username=user.username, password='test')
        return self.client.post(url, *args, **kwargs)

    def test_not_logged_in(self):
        period = PeriodBuilder.quickadd_ducku_duck1010_active()
        url = self._get_url(period.period.id)
        expected_url = "http://testserver/authenticate/login?next=/devilry_student/browse/period/{}".format(period.period.id)
        response = self.client.get(url)
        self.assertRedirects(response, 
            expected_url=expected_url, 
            status_code=302, target_status_code=200)

    def test_assignment_list(self):
        period = PeriodBuilder.quickadd_ducku_duck1010_active()
        
        groupbuilder1 = period.add_assignment('assignment1')\
        .add_group(students=[self.testuser])
        groupbuilder2 = period.add_assignment('assignment2')\
        .add_group(students=[self.testuser])        
        period.add_relatedstudents(self.testuser)

        response = self._getas(self.testuser, id=period.period.id)
        html = response.content
        self.assertEquals(len(cssFind(html, '.assignment-list-element')), 2)

    def test_no_assignments(self):
        period = PeriodBuilder.quickadd_ducku_duck1010_active()
        
        groupbuilder1 = period.add_assignment('assignment1')\
        .add_group(students=[self.testuser])
        groupbuilder2 = period.add_assignment('assignment2')\
        .add_group(students=[self.testuser])        
        period.add_relatedstudents(self.testuser)

        johndoe = UserBuilder('johndoe').user

        response = self._getas(johndoe, id=period.period.id)
        html = response.content
        self.assertEquals(len(cssFind(html, '.assignment-list-element')), 0)


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

    def test_get_qualifiesforexam_noe(self):
        period = PeriodBuilder.quickadd_ducku_duck1010_active()
        
        groupbuilder = period.add_assignment('assignment1')\
        .add_group(students=[self.testuser])
        period.add_relatedstudents(self.testuser)

        deadline1builder = groupbuilder.add_deadline_x_weeks_ago(weeks=4)
        delivery1 = deadline1builder.add_delivery_x_hours_before_deadline(hours=10).delivery

        response = self._getas(self.testuser, id=period.period.id)
        html = response.content
        self.assertEquals(response.status_code, 200)

        self.assertEquals(len(cssFind(html, '.qualifies-for-exams')), 0)  

    def test_get_qualifiesforexam_notready(self):
        period = PeriodBuilder.quickadd_ducku_duck1010_active()
        
        groupbuilder = period.add_assignment('assignment1')\
        .add_group(students=[self.testuser])
        period.add_relatedstudents(self.testuser)

        deadline1builder = groupbuilder.add_deadline_x_weeks_ago(weeks=4)
        delivery1 = deadline1builder.add_delivery_x_hours_before_deadline(hours=10).delivery

        relatedstudent = period.period.relatedstudent_set.get(user=self.testuser)

        status = Status.objects.create(period=period.period,
                user=self.testuser,
                status=Status.NOTREADY)
        status.students.create(relatedstudent=relatedstudent, qualifies=False)

        response = self._getas(self.testuser, id=period.period.id)
        html = response.content
        self.assertEquals(response.status_code, 200)

        self.assertEquals(len(cssFind(html, '.qualifies-for-exams')), 0)
