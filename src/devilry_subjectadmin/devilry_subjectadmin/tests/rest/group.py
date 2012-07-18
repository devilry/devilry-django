from dingus import Dingus
from datetime import datetime
from django.test import TestCase

from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Candidate
from devilry.apps.core.models import Examiner
from devilry.apps.core.models import AssignmentGroupTag
from devilry.apps.core.models import Deadline
from devilry.utils.rest_testclient import RestClient

from devilry_subjectadmin.rest.errors import PermissionDeniedError
from devilry_subjectadmin.rest.group import GroupDao
from devilry_subjectadmin.rest.group import GroupListingAggregator



class TestGroupListingAggator(TestCase):
    def create_testassignments(self):
        testhelper = TestHelper()
        testhelper.add(nodes='uni',
                       subjects=['duck1010'],
                       periods=['firstsem'],
                       assignments=['a1', 'a2'])
        testhelper.create_superuser("superuser")
        return testhelper

    def test_tull(self):
        testhelper = self.create_testdata()
        assignment1 = testhelper.duck1010_firstsem_a1
        for assignment in GroupListingAggregator().tull(assignment1.id):
            print assignment.deadlines.all()

    def create_testdata(self):
        testhelper = self.create_testassignments()

        for num in xrange(3):
            path = 'uni;duck1010.firstsem.a1.g{num}:candidate(student{num}):examiner(examiner1).d1'
            testhelper.add_to_path(path.format(**vars()))
            group = getattr(testhelper, 'duck1010_firstsem_a1_g{0}'.format(num))
            group.tags.create(tag="stuff")
            group.tags.create(tag="lownumber")
            delivery = testhelper.add_delivery(group)
            testhelper.add_feedback(delivery,
                                    verdict=dict(grade='A', points=100, is_passing_grade=True))
        return testhelper

    def test_read(self):
        testhelper = self.create_testdata()
        assignment1 = testhelper.duck1010_firstsem_a1
        groups = GroupListingAggregator().list(assignment1.id)
        # We only check a few values here. The most important thing is that the
        # database queries are sane, since the other stuff is tested in
        # smaller units
        self.assertEquals(len(groups), 3)
        self.assertTrue('examiners' in groups[0].keys())
        self.assertTrue('students' in groups[0].keys())
        self.assertTrue('deadlines' in groups[0].keys())
        fields = set(['id', 'name', 'is_open', 'feedback__grade', 'feedback__points',
                      'feedback__is_passing_grade', 'feedback__save_timestamp',
                      'examiners', 'students', 'tags', 'deadlines', 'num_deliveries'])
        self.assertEquals(set(groups[0].keys()), fields)
        self.assertEquals(AssignmentGroup.objects.get(id=groups[0]['id']).parentnode_id,
                          assignment1.id)




class TestCreateStuff(TestCase):
    def test_create_noauth_minimal(self):
        testhelper = self.create_testassignments()
        assignment1 = testhelper.duck1010_firstsem_a1
        group = GroupListingAggregator().create(assignment1.id)
        group_db = AssignmentGroup.objects.get(id=group.id) # Raises exception if not found
        self.assertEquals(group_db.name, None)
        self.assertEquals(group_db.is_open, True)

    def test_create_noauth_simpleattrs(self):
        testhelper = self.create_testassignments()
        assignment1 = testhelper.duck1010_firstsem_a1
        group = GroupListingAggregator().create(assignment1.id, name='Somename', is_open=False)
        group_db = AssignmentGroup.objects.get(id=group.id) # Raises exception if not found
        self.assertEquals(group_db.name, 'Somename')
        self.assertEquals(group_db.is_open, False)

    def test_get_user(self):
        with self.assertRaises(ValueError):
            GroupListingAggregator()._get_user('tstuser')
        testhelper = TestHelper()
        tstuser = testhelper.create_user('tstuser')
        GroupListingAggregator()._get_user('tstuser')


    def test_create_candidate_from_studentdict(self):
        testhelper = self.create_testassignments()
        assignment1 = testhelper.duck1010_firstsem_a1
        group = AssignmentGroup(parentnode=assignment1)
        group.save()
        tstuser = testhelper.create_user('tstuser')
        candidate = GroupDao()._create_candidate_from_studentdict(group, dict(student__username='tstuser'))
        self.assertEquals(candidate.student.username, 'tstuser')
        self.assertEquals(candidate.candidate_id, None)
        candidate = GroupDao()._create_candidate_from_studentdict(group,
                                                                  dict(student__username='tstuser',
                                                                       candidate_id='XY'))
        self.assertEquals(candidate.student.username, 'tstuser')
        self.assertEquals(candidate.candidate_id, 'XY')
        candidate_db = Candidate.objects.get(id=candidate.id) # Raises exception if not found
        self.assertEquals(candidate_db.student.username, 'tstuser')

    def test_create_candidate_from_studentdict_errors(self):
        with self.assertRaises(ValueError):
            GroupDao()._create_candidate_from_studentdict(None, []) # not a dict
        with self.assertRaises(ValueError):
            GroupDao()._create_candidate_from_studentdict(None, {}) # username not in dict

    def test_create_noauth_students(self):
        testhelper = self.create_testassignments()
        assignment1 = testhelper.duck1010_firstsem_a1
        tstuser = testhelper.create_user('tstuser')
        tstuser = testhelper.create_user('tstuser2')
        group = GroupDao().create(assignment1.id, students=[{'student__username': 'tstuser'},
                                                                {'student__username': 'tstuser2'}])
        group_db = AssignmentGroup.objects.get(id=group.id) # Raises exception if not found
        usernames = [candidate.student.username for candidate in group.candidates.all()]
        self.assertEquals(set(usernames), set(['tstuser', 'tstuser2']))



    def test_create_examiner_from_examinerdict(self):
        testhelper = self.create_testassignments()
        assignment1 = testhelper.duck1010_firstsem_a1
        group = AssignmentGroup(parentnode=assignment1)
        group.save()
        tstuser = testhelper.create_user('tstuser')
        examiner = GroupDao()._create_examiner_from_examinerdict(group, dict(username='tstuser'))
        self.assertEquals(examiner.user.username, 'tstuser')
        examiner_db = Examiner.objects.get(id=examiner.id) # Raises exception if not found
        self.assertEquals(examiner_db.user.username, 'tstuser')

    def test_create_examiner_from_examinerdict_errors(self):
        with self.assertRaises(ValueError):
            GroupDao()._create_examiner_from_examinerdict(None, []) # not a dict
        with self.assertRaises(ValueError):
            GroupDao()._create_examiner_from_examinerdict(None, {}) # username not in dict

    def test_create_noauth_examiners(self):
        testhelper = self.create_testassignments()
        assignment1 = testhelper.duck1010_firstsem_a1
        tstuser = testhelper.create_user('tstuser')
        tstuser = testhelper.create_user('tstuser2')
        group = GroupDao().create(assignment1.id, examiners=[{'username': 'tstuser'},
                                                                {'username': 'tstuser2'}])
        group_db = AssignmentGroup.objects.get(id=group.id) # Raises exception if not found
        usernames = [examiner.user.username for examiner in group.examiners.all()]
        self.assertEquals(set(usernames), set(['tstuser', 'tstuser2']))



    def test_create_tag_from_tagdict(self):
        testhelper = self.create_testassignments()
        assignment1 = testhelper.duck1010_firstsem_a1
        group = AssignmentGroup(parentnode=assignment1)
        group.save()
        tag = GroupDao()._create_tag_from_tagdict(group, dict(tag='mytag'))
        self.assertEquals(tag.tag, 'mytag')
        tag_db = AssignmentGroupTag.objects.get(id=tag.id) # Raises exception if not found
        self.assertEquals(tag_db.tag, 'mytag')

    def test_create_tag_from_tagdict_errors(self):
        with self.assertRaises(ValueError):
            GroupDao()._create_tag_from_tagdict(None, []) # not a dict
        with self.assertRaises(ValueError):
            GroupDao()._create_tag_from_tagdict(None, {}) # username not in dict

    def test_create_noauth_tags(self):
        testhelper = self.create_testassignments()
        assignment1 = testhelper.duck1010_firstsem_a1
        group = GroupDao().create(assignment1.id, tags=[{'tag': 'tag1'},
                                                            {'tag': 'tag2'}])
        group_db = AssignmentGroup.objects.get(id=group.id) # Raises exception if not found
        tags = [tag.tag for tag in group.tags.all()]
        self.assertEquals(set(tags), set(['tag1', 'tag2']))



    def test_create_deadline_from_deadlinedict(self):
        testhelper = self.create_testassignments()
        assignment1 = testhelper.duck1010_firstsem_a1
        group = AssignmentGroup(parentnode=assignment1)
        group.save()
        deadline = GroupDao()._create_deadline_from_deadlinedict(group,
                                                                 dict(deadline=datetime(2010, 1, 2, 3, 4, 5)))
        self.assertEquals(deadline.deadline, datetime(2010, 1, 2, 3, 4, 5))
        deadline_db = Deadline.objects.get(id=deadline.id) # Raises exception if not found
        self.assertEquals(deadline_db.deadline, datetime(2010, 1, 2, 3, 4, 5))

    def test_create_deadline_from_deadlinedict_errors(self):
        with self.assertRaises(ValueError):
            GroupDao()._create_deadline_from_deadlinedict(None, []) # not a dict
        with self.assertRaises(ValueError):
            GroupDao()._create_deadline_from_deadlinedict(None, {}) # username not in dict

    def test_create_noauth_deadlines(self):
        testhelper = self.create_testassignments()
        assignment1 = testhelper.duck1010_firstsem_a1
        group = GroupDao().create(assignment1.id, deadlines=[{'deadline': datetime(2010, 1, 2, 3, 4, 5)},
                                                                    {'deadline': datetime(2010, 2, 3, 4, 5, 6)}])
        group_db = AssignmentGroup.objects.get(id=group.id) # Raises exception if not found
        deadlines = [deadline.deadline for deadline in group.deadlines.all()]
        self.assertEquals(set(deadlines),
                          set([datetime(2010, 1, 2, 3, 4, 5), datetime(2010, 2, 3, 4, 5, 6)]))

    def test_create(self):
        testhelper = self.create_testassignments()
        assignment1 = testhelper.duck1010_firstsem_a1
        group = GroupDao().create(assignment1.id, name='Superprojectgroup')
        group_db = AssignmentGroup.objects.get(id=group.id) # Raises exception if not found
        self.assertEquals(group_db.name, 'Superprojectgroup')
        self.assertEquals(group_db.is_open, True)




class TestListOrCreateGroupRest(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1'],
                            assignments=['a1:admin(a1admin)'])
        self.client = RestClient()
        self.testhelper.create_user('student0')
        self.a1url = '/devilry_subjectadmin/rest/group/{0}/'.format(self.testhelper.sub_p1_a1.id)

    def test_list(self):
        self.client.login(username='a1admin', password='test')
        for studentNum in xrange(3):
            path = 'uni;sub.p1.a1.g{studentNum}:candidate(stud{studentNum})'.format(studentNum=studentNum)
            self.testhelper.add_to_path(path)
        content, response = self.client.rest_get(self.a1url)
        self.assertEquals(len(content), 3)
        self.assertEquals(set(content[0].keys()),
                          set([u'name', u'tags', u'students',
                               u'feedback__is_passing_grade', u'deadlines',
                               u'id', u'feedback__points', u'feedback__grade',
                               u'is_open', u'num_deliveries',
                               u'feedback__save_timestamp', u'examiners']))

    def test_create(self):
        self.client.login(username='a1admin', password='test')
        data = dict(
                    students=[dict(candidate_id=u'candid334',
                                   student__username=u'student0',
                                   student__email=u'myemail2',
                                   student__devilryuserprofile__full_name=u'Somename2')],
                    tags=[dict(tag='group1')],
                    deadlines=[dict(deadline=u'2011-01-02 03:04:05')]
                   )
        content, response = self.client.rest_post(self.a1url, data)
        self.assertEquals(response.status_code, 201)
        self.assertEquals(content.keys(), ['id'])
        groups = self.testhelper.sub_p1_a1.assignmentgroups.all()
        self.assertEquals(len(groups), 1)
        self.assertEquals(content['id'], groups[0].id)

    def test_noperm(self):
        self.client.login(username='student0', password='test')
        content, response = self.client.rest_post(self.a1url, {})
        self.assertEquals(response.status_code, 403)
        self.assertEquals(content, {u'detail': u'Permission denied'})


class TestInstanceGroupRest(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1'],
                            assignments=['a1:admin(a1admin)'])
        self.client = RestClient()
        self.testhelper.create_user('student0')

    def _geturl(self, group_id, assignment_id=None):
        assignment_id = assignment_id or self.testhelper.sub_p1_a1.id
        return '/devilry_subjectadmin/rest/group/{0}/{1}'.format(assignment_id, group_id)

    def _putas(self, username, group_id, assignment_id=None, data={}):
        self.client.login(username=username, password='test')
        return self.client.rest_put(self._geturl(assignment_id, group_id), data)

    def _add_group(self, name, candidates, examiners):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate({candidates}):examiner({examiners})'.format(**vars()))
        return getattr(self.testhelper, 'sub_p1_a1_' + name)

    def test_put(self):
        g1 = self._add_group('g1', 'student0', 'examiner0')
        content, response = self._putas('a1admin', g1.id)
        print response
        #print content
