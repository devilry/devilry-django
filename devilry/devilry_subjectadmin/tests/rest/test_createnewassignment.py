from datetime import timedelta

from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.devilry_subjectadmin.rest.createnewassignment import CreateNewAssignmentDao
from devilry.devilry_subjectadmin.rest.errors import BadRequestFieldError
from devilry.devilry_rest.testclient import RestClient
from devilry.apps.core.models.deliverytypes import NON_ELECTRONIC
from devilry.apps.core.models.deliverytypes import ELECTRONIC
from .common import isoformat_datetime


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
                                            delivery_types=ELECTRONIC, anonymous=False)
        self.assertEquals(assignment.short_name, 'a1')
        self.assertEquals(assignment.long_name, 'Assignment 1')
        self.assertEquals(assignment.publishing_time, publishing_time)
        self.assertEquals(assignment.first_deadline,
                          first_deadline.replace(microsecond=0, tzinfo=None))
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

    def test_create_group_from_relatedstudent_non_electronic(self):
        dao = CreateNewAssignmentDao()
        self.testhelper.add_to_path('uni;sub.p1.a1')
        related_louie = self._create_related_student('louie')
        a1 = self.testhelper.sub_p1_a1
        a1.delivery_types = NON_ELECTRONIC
        group = dao._create_group_from_relatedstudent(a1, related_louie, [])
        self.assertEquals(group.deadlines.count(), 1)


    def test_setupstudents_allrelated(self):
        self._create_related_student('louie')
        self._create_related_student('dewey', candidate_id='dew123')
        dao = CreateNewAssignmentDao()
        self.testhelper.add_to_path('uni;sub.p1.a1')

        self.assertEquals(self.testhelper.sub_p1_a1.assignmentgroups.count(), 0)
        deadline = self.testhelper.sub_p1_a1.publishing_time + timedelta(days=1)
        dao._setup_students(self.testhelper.sub_p1_a1,
                            first_deadline=deadline,
                            setupstudents_mode='allrelated',
                            setupexaminers_mode='do_not_setup')
        self.assertEquals(self.testhelper.sub_p1_a1.assignmentgroups.count(), 2)

        groups = list(self.testhelper.sub_p1_a1.assignmentgroups.all().order_by('candidates__student__username'))
        self.assertEquals(groups[0].candidates.all()[0].student.username, 'dewey')
        self.assertEquals(groups[0].candidates.all()[0].candidate_id, 'dew123')
        self.assertEquals(groups[1].candidates.all()[0].student.username, 'louie')
        self.assertEquals(groups[1].candidates.all()[0].candidate_id, None)

        self.assertEquals(groups[0].deadlines.all().count(), 1)
        self.assertEquals(groups[1].deadlines.all().count(), 1)
        self.assertEquals(groups[0].deadlines.all()[0].deadline, deadline)

    def test_setupstudents_allrelated_examiners_bytags(self):
        self._create_related_student('louie', tags='bb,aa')
        self._create_related_examiner('examiner2', tags='aa,cc')
        dao = CreateNewAssignmentDao()
        self.testhelper.add_to_path('uni;sub.p1.a1')

        deadline = self.testhelper.sub_p1_a1.publishing_time + timedelta(days=1)
        dao._setup_students(self.testhelper.sub_p1_a1,
                            first_deadline=deadline,
                            setupstudents_mode='allrelated',
                            setupexaminers_mode='bytags')
        group = self.testhelper.sub_p1_a1.assignmentgroups.all()[0]
        self.assertEquals(group.examiners.all().count(), 1)

    def test_setupstudents_copyfromassignment(self):
        dao = CreateNewAssignmentDao()
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1;secret):tags(good,super)')
        self.testhelper.add_to_path('uni;sub.p1.a1.g2:candidate(student2,student3)')
        self.testhelper.add_to_path('uni;sub.p1.a2')
        deadline = self.testhelper.sub_p1_a1.publishing_time + timedelta(days=1)

        self.assertEquals(self.testhelper.sub_p1_a1.assignmentgroups.count(), 2)
        self.assertEquals(self.testhelper.sub_p1_a2.assignmentgroups.count(), 0)
        dao._setup_students(self.testhelper.sub_p1_a2,
                            first_deadline=deadline,
                            copyfromassignment_id=self.testhelper.sub_p1_a1.id,
                            setupstudents_mode='copyfromassignment',
                            setupexaminers_mode='do_not_setup')
        self.assertEquals(self.testhelper.sub_p1_a2.assignmentgroups.count(), 2)

        groups = list(self.testhelper.sub_p1_a2.assignmentgroups.all().order_by('candidates__student__username'))
        self.assertEquals(groups[0].name, 'g1')
        self.assertEquals(groups[0].candidates.all()[0].student.username, 'student1')
        self.assertEquals(groups[0].candidates.all()[0].candidate_id, 'secret')
        self.assertEquals(set([t.tag for t in groups[0].tags.all()]),
                          set(['good', 'super']))
        self.assertEquals(groups[1].name, 'g2')
        self.assertEquals(set([c.student.username for c in groups[1].candidates.all()]),
                          set(['student2', 'student3']))
        self.assertEquals(groups[1].tags.count(), 0)

        self.assertEquals(groups[0].deadlines.all().count(), 1)
        self.assertEquals(groups[1].deadlines.all().count(), 1)
        self.assertEquals(groups[0].deadlines.all()[0].deadline, deadline)

    def test_setupstudents_copyfromassignment_onlypassing(self):
        dao = CreateNewAssignmentDao()
        self.testhelper.add_to_path('uni;sub.p1.a1.awesome:candidate(student1):examiner(examiner1).d1')
        self.testhelper.add_to_path('uni;sub.p1.a1.failer:candidate(student2):examiner(examiner2).d1')
        self.testhelper.add_to_path('uni;sub.p1.a1.nofeedback:candidate(student3)')
        self.testhelper.add_delivery(self.testhelper.sub_p1_a1_awesome,
                                     {'f.py': ['print ', 'yeh']})
        self.testhelper.add_feedback(self.testhelper.sub_p1_a1_awesome,
                                     verdict={'grade': 'A', 'points': 100, 'is_passing_grade': True})
        self.testhelper.add_delivery(self.testhelper.sub_p1_a1_failer,
                                     {'f.py': ['print ', 'meh']})
        self.testhelper.add_feedback(self.testhelper.sub_p1_a1_failer,
                                     verdict={'grade': 'F', 'points': 1, 'is_passing_grade': False})

        self.testhelper.add_to_path('uni;sub.p1.a2')
        deadline = self.testhelper.sub_p1_a1.publishing_time + timedelta(days=1)
        self.assertEquals(self.testhelper.sub_p1_a1.assignmentgroups.count(), 3)
        self.assertEquals(self.testhelper.sub_p1_a2.assignmentgroups.count(), 0)

        dao._setup_students(self.testhelper.sub_p1_a2,
                            first_deadline=deadline,
                            copyfromassignment_id=self.testhelper.sub_p1_a1.id,
                            only_copy_passing_groups=True,
                            setupstudents_mode='copyfromassignment',
                            setupexaminers_mode='do_not_setup')
        self.assertEquals(self.testhelper.sub_p1_a2.assignmentgroups.count(), 1)

        group = self.testhelper.sub_p1_a2.assignmentgroups.all()[0]
        self.assertEquals(group.name, 'awesome')

    def test_setupstudents_copyfromassignment_withexaminers(self):
        dao = CreateNewAssignmentDao()
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1):examiner(examiner1,examiner2)')
        self.testhelper.add_to_path('uni;sub.p1.a2')
        deadline = self.testhelper.sub_p1_a1.publishing_time + timedelta(days=1)

        dao._setup_students(self.testhelper.sub_p1_a2,
                            first_deadline=deadline,
                            copyfromassignment_id=self.testhelper.sub_p1_a1.id,
                            setupstudents_mode='copyfromassignment',
                            setupexaminers_mode='copyfromassignment')
        self.assertEquals(self.testhelper.sub_p1_a2.assignmentgroups.count(), 1)

        group = self.testhelper.sub_p1_a2.assignmentgroups.all()[0]
        self.assertEquals(set([c.user.username for c in group.examiners.all()]),
                          set(['examiner1', 'examiner2']))

    def test_setupstudents_copyfromassignment_outofperiod(self):
        dao = CreateNewAssignmentDao()
        self.testhelper.add_to_path('uni;sub.p1.a1')
        self.testhelper.add_to_path('uni;sub.p2.a1')
        deadline = self.testhelper.sub_p1_a1.publishing_time + timedelta(days=1)

        with self.assertRaises(BadRequestFieldError):
            dao._setup_students(self.testhelper.sub_p1_a1,
                                first_deadline=deadline,
                                copyfromassignment_id=self.testhelper.sub_p2_a1.id,
                                setupstudents_mode='copyfromassignment',
                                setupexaminers_mode='copyfromassignment')

    def test_setupstudents_copyfromassignment_make_authuser_examiner(self):
        dao = CreateNewAssignmentDao()
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(student1)')
        self.testhelper.add_to_path('uni;sub.p1.a2')
        deadline = self.testhelper.sub_p1_a1.publishing_time + timedelta(days=1)

        user = self.testhelper.create_user('superhero')
        dao._setup_students(self.testhelper.sub_p1_a2,
                            first_deadline=deadline,
                            copyfromassignment_id=self.testhelper.sub_p1_a1.id,
                            setupstudents_mode='copyfromassignment',
                            setupexaminers_mode='make_authenticated_user_examiner',
                            user=user)
        self.assertEquals(self.testhelper.sub_p1_a2.assignmentgroups.count(), 1)

        group = self.testhelper.sub_p1_a2.assignmentgroups.all()[0]
        self.assertEquals(set([c.user.username for c in group.examiners.all()]),
                          set(['superhero']))


class TestRestCreateNewAssignmentIntegration(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1:admin(p1admin)', 'p2'])
        self.client = RestClient()
        self.url = '/devilry_subjectadmin/rest/createnewassignment/'

    def _login_p1admin(self):
        self.client.login(username='p1admin', password='test')


    def _get_testdata(self):
        publishing_time = self.testhelper.sub_p1.start_time + timedelta(days=1)
        first_deadline = self.testhelper.sub_p1.start_time + timedelta(days=2)
        return dict(period_id=self.testhelper.sub_p1.id,
                    short_name='a', long_name='Aa',
                    first_deadline=isoformat_datetime(first_deadline),
                    publishing_time=isoformat_datetime(publishing_time),
                    delivery_types=ELECTRONIC, anonymous=False,
                    setupstudents_mode='do_not_setup',
                    setupexaminers_mode='do_not_setup')

    def test_create(self):
        self._login_p1admin()
        publishing_time = self.testhelper.sub_p1.start_time + timedelta(days=1)
        first_deadline = self.testhelper.sub_p1.start_time + timedelta(days=2)
        content, response = self.client.rest_post(self.url, self._get_testdata())
        self.assertEquals(response.status_code, 201)
        self.assertEquals(set(content.keys()),
                          set(['id', 'period_id', 'short_name', 'long_name', 'first_deadline', 'anonymous']))

    def test_create_notfound(self):
        self._login_p1admin()
        data = self._get_testdata()
        data['period_id'] = 200000
        content, response = self.client.rest_post(self.url, data)
        self.assertEquals(response.status_code, 403)

    def test_create_permissiondenied(self):
        self.testhelper.create_user('nopermsuser')
        self.client.login(username='nopermsuser', password='test')
        data = self._get_testdata()
        content, response = self.client.rest_post(self.url, data)
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
        data = self._get_testdata()
        data['first_deadline'] = None
        data['setupstudents_mode'] = 'allrelated'
        content, response = self.client.rest_post(self.url, data)
        self.assertEquals(response.status_code, 400)
        self.assertTrue(content['field_errors']['first_deadline'][0].startswith('Required when adding'))
