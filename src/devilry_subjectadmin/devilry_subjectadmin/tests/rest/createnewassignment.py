from datetime import timedelta, datetime
from dingus import Dingus
from django.test import TestCase
import json
from django.contrib.auth.models import User

from devilry.apps.core.testhelper import TestHelper
from devilry_subjectadmin.rest.createnewassignment import CreateNewAssignmentDao
from devilry_subjectadmin.rest.errors import PermissionDeniedError
from devilry.utils.rest_testclient import RestClient


def isoformat_datetime(datetimeobj):
    return datetimeobj.strftime('%Y-%m-%d %H:%M:%S')


class TestRestCreateNewAssignmentDao(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:admin(p1admin)', 'p2'])
        self.testhelper.create_superuser("superuser")

    def test_create_assignment(self):
        dao = CreateNewAssignmentDao()
        publishing_time = self.testhelper.sub_p1.start_time + timedelta(days=1)
        first_deadline = self.testhelper.sub_p1.start_time + timedelta(days=2)
        assignment = dao._create_assignment(period=self.testhelper.sub_p1,
                                            short_name='a1', long_name='Assignment 1',
                                            first_deadline = first_deadline,
                                            publishing_time=publishing_time,
                                            delivery_types=0, anonymous=False)
        self.assertEquals(assignment.short_name, 'a1')
        self.assertEquals(assignment.long_name, 'Assignment 1')
        self.assertEquals(assignment.publishing_time, publishing_time)
        self.assertEquals(assignment.first_deadline, first_deadline)
        self.assertEquals(assignment.delivery_types, 0)
        self.assertEquals(assignment.anonymous, False)

    def _create_related_student(self, username, candidate_id=None, tags=None):
        user = self.testhelper.create_user(username)
        relatedstudent = self.testhelper.sub_p1.relatedstudent_set.create(user=user,
                                                                          candidate_id=candidate_id)
        if tags:
            relatedstudent.tags = tags
            relatedstudent.save()
        return relatedstudent

    def _create_related_examiner(self, username, tags=None):
        user = self.testhelper.create_user(username)
        relatedexaminer = self.testhelper.sub_p1.relatedexaminer_set.create(user=user)
        if tags:
            relatedexaminer.tags = tags
            relatedexaminer.save()
        return relatedexaminer

    def test_create_group_from_relatedstudent(self):
        dao = CreateNewAssignmentDao()
        self.testhelper.add_to_path('uni;sub.p1.a1')
        related_louie = self._create_related_student('louie')
        group = dao._create_group_from_relatedstudent(self.testhelper.sub_p1_a1, related_louie, [])
        self.assertEquals(group.candidates.all()[0].student.username, 'louie')
        self.assertEquals(group.candidates.all()[0].candidate_id, None)

        related_dewey = self._create_related_student('dewey', candidate_id='dew123',
                                                     tags='bb,aa')
        related_examiner1 = self._create_related_examiner('examiner1', tags='cc,dd')
        related_examiner2 = self._create_related_examiner('examiner2', tags='aa')
        group = dao._create_group_from_relatedstudent(self.testhelper.sub_p1_a1, related_dewey,
                                                      [related_examiner1, related_examiner2])
        self.assertEquals(group.candidates.all()[0].candidate_id, 'dew123')
        self.assertEquals(group.examiners.all().count(), 1)
        tags = group.tags.all().order_by('tag')
        self.assertEquals(len(tags), 2)
        self.assertEquals(tags[0].tag, 'aa')
        self.assertEquals(tags[1].tag, 'bb')

    def test_add_all_relatedstudents(self):
        self._create_related_student('louie')
        self._create_related_student('dewey', candidate_id='dew123')
        dao = CreateNewAssignmentDao()
        self.testhelper.add_to_path('uni;sub.p1.a1')

        self.assertEquals(self.testhelper.sub_p1_a1.assignmentgroups.count(), 0)
        deadline = self.testhelper.sub_p1_a1.publishing_time + timedelta(days=1)
        dao._add_all_relatedstudents(self.testhelper.sub_p1_a1, deadline, False)
        self.assertEquals(self.testhelper.sub_p1_a1.assignmentgroups.count(), 2)

        groups = list(self.testhelper.sub_p1_a1.assignmentgroups.all().order_by('candidates__student__username'))
        self.assertEquals(groups[0].candidates.all()[0].student.username, 'dewey')
        self.assertEquals(groups[0].candidates.all()[0].candidate_id, 'dew123')
        self.assertEquals(groups[1].candidates.all()[0].student.username, 'louie')
        self.assertEquals(groups[1].candidates.all()[0].candidate_id, None)

        self.assertEquals(groups[0].deadlines.all().count(), 1)
        self.assertEquals(groups[1].deadlines.all().count(), 1)
        self.assertEquals(groups[0].deadlines.all()[0].deadline, deadline)

    def test_add_all_relatedstudents_autosetup_examiners(self):
        self._create_related_student('louie', tags='bb,aa')
        self._create_related_examiner('examiner2', tags='aa,cc')
        dao = CreateNewAssignmentDao()
        self.testhelper.add_to_path('uni;sub.p1.a1')

        deadline = self.testhelper.sub_p1_a1.publishing_time + timedelta(days=1)
        dao._add_all_relatedstudents(self.testhelper.sub_p1_a1, deadline,
                                     autosetup_examiners=True)
        group = self.testhelper.sub_p1_a1.assignmentgroups.all()[0]
        self.assertEquals(group.examiners.all().count(), 1)



class TestRestCreateNewAssignmentIntegration(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:admin(p1admin)', 'p2'])
        self.client = RestClient()
        p1admin = User.objects.get(username='p1admin')
        self.urlformat = '/devilry_subjectadmin/rest/createnewassignment/{period_id}/'
        self.url = self.urlformat.format(period_id=self.testhelper.sub_p1.id)

    def _login_p1admin(self):
        self.client.login(username='p1admin', password='test')

    def test_create(self):
        self._login_p1admin()
        publishing_time = self.testhelper.sub_p1.start_time + timedelta(days=1)
        first_deadline = self.testhelper.sub_p1.start_time + timedelta(days=2)
        data = dict(short_name='a', long_name='Aa',
                    first_deadline=isoformat_datetime(first_deadline),
                    publishing_time=isoformat_datetime(publishing_time),
                    delivery_types=0, anonymous=False,
                    add_all_relatedstudents=False,
                    autosetup_examiners=False)
        content, response = self.client.rest_post(self.url, data)
        self.assertEquals(response.status_code, 201)
        self.assertEquals(content.keys(), ['id'])

    def test_create_notfound(self):
        self._login_p1admin()
        invalidurl = self.urlformat.format(period_id=20000)
        content, response = self.client.rest_post(invalidurl, {})
        self.assertEquals(response.status_code, 403)

    def test_create_permissiondenied(self):
        self.testhelper.create_user('nopermsuser')
        self.client.login(username='nopermsuser', password='test')
        content, response = self.client.rest_post(self.url, {})
        self.assertEquals(response.status_code, 403)

    def test_create_validation(self):
        self._login_p1admin()
        content, response = self.client.rest_post(self.url, {})
        self.assertEquals(response.status_code, 400)
        self.assertEquals(content.keys(), ['field_errors'])
        for fieldname in ['delivery_types', 'long_name', 'publishing_time', 'short_name']:
            self.assertEquals(content['field_errors'][fieldname], [u'This field is required.'])

    def test_create_first_deadline_none(self):
        self._login_p1admin()
        publishing_time = self.testhelper.sub_p1.start_time + timedelta(days=1)
        first_deadline = self.testhelper.sub_p1.start_time + timedelta(days=2)
        data = dict(short_name='a', long_name='Aa',
                    first_deadline=None,
                    publishing_time=isoformat_datetime(publishing_time),
                    delivery_types=0, anonymous=False,
                    add_all_relatedstudents=True,
                    autosetup_examiners=False)
        content, response = self.client.rest_post(self.url, data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(content['field_errors']['first_deadline'],
                          [u'Required when automatically adding related students'])
