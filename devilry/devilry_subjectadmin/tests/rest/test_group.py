from urllib import urlencode
from datetime import datetime

from django.test import TestCase
from django.core.exceptions import ValidationError

from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_rest.testclient import RestClient
from devilry.devilry_subjectadmin.rest.group import GroupManager
from devilry.devilry_subjectadmin.rest.errors import PermissionDeniedError


class TestListGroupRest(TestCase):
    def setUp(self):
        self.testhelper = TestHelper()
        self.client = RestClient()

    def _geturl(self, assignment_id):
        assignment_id = assignment_id or self.testhelper.sub_p1_a1.id
        return '/devilry_subjectadmin/rest/group/{0}/'.format(assignment_id)

    def _getas(self, username, assignment_id, **data):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self._geturl(assignment_id), **data)

    def _create_testassignments(self):
        self.testhelper.add(nodes='uni',
                       subjects=['duck1010'],
                       periods=['firstsem'],
                       assignments=['a1:admin(a1admin)', 'a2'])

    def _create_testdata(self):
        self._create_testassignments()
        for num in xrange(3):
            path = 'uni;duck1010.firstsem.a1.g{num}:candidate(student{num},extrastudent):examiner(examiner1,extraexaminer).d1'
            self.testhelper.add_to_path(path.format(**vars()))
            group = getattr(self.testhelper, 'duck1010_firstsem_a1_g{0}'.format(num))
            group.tags.create(tag="stuff")
            group.tags.create(tag="lownumber")
            delivery = self.testhelper.add_delivery(group)
            if num != 2:
                self.testhelper.add_feedback(delivery,
                                             verdict=dict(grade='A', points=100,
                                                          is_passing_grade=True))

    def test_list_permissiondenied(self):
        self.testhelper.create_user('nobody')
        self._create_testassignments()
        a1 = self.testhelper.duck1010_firstsem_a1
        content, response = self._getas('nobody', a1.id)
        self.assertEquals(response.status_code, 403)


    def _test_list_as(self, username):
        self._create_testdata()
        a1 = self.testhelper.duck1010_firstsem_a1
        content, response = self._getas(username, a1.id)
        #from pprint import pprint
        #pprint(content)

        self.assertEquals(len(content), 3)
        self.assertEquals(set(content[0].keys()),
                          set(['name', 'feedback', 'deadlines', 'id', 'etag', 'status',
                               'is_open', 'parentnode', 'candidates', 'tags',
                               'examiners', 'num_deliveries']))

        # Properties directly from group
        self.assertEquals(AssignmentGroup.objects.get(id=content[0]['id']).parentnode_id,
                          a1.id)
        self.assertEquals(content[0]['is_open'], False)
        self.assertEquals(content[0]['name'], 'g0')
        self.assertEquals(content[0]['num_deliveries'], 1)
        self.assertEquals(content[0]['parentnode'], a1.id)

        # Feedback
        feedback = content[0]['feedback']
        self.assertEquals(set(feedback.keys()),
                          set(['id', 'grade', 'is_passing_grade', 'points', 'save_timestamp',
                               'delivery_id']))
        self.assertEquals(feedback['grade'], 'A')
        self.assertEquals(feedback['is_passing_grade'], True)
        self.assertEquals(feedback['points'], 100)

        # NULL feedback
        self.assertEquals(content[2]['feedback'], None)

        # Canididates
        def get_usernames(users):
            return [user['user']['username'] for user in users]
        self.assertEquals(len(content[0]['candidates']), 2)
        self.assertEquals(set(get_usernames(content[0]['candidates'])),
                          set(['student0', 'extrastudent']))
        self.assertEquals(set(content[0]['candidates'][0].keys()),
                          set(['id', 'candidate_id', 'user']))
        self.assertEquals(set(content[0]['candidates'][0]['user'].keys()),
                          set(['email', 'full_name', 'id', 'username', 'displayname']))

        # Examiners
        self.assertEquals(len(content[0]['examiners']), 2)
        self.assertEquals(set(get_usernames(content[0]['examiners'])),
                          set(['examiner1', 'extraexaminer']))
        self.assertEquals(set(content[0]['examiners'][0].keys()),
                          set(['id', 'user']))
        self.assertEquals(set(content[0]['examiners'][0]['user'].keys()),
                          set(['email', 'full_name', 'id', 'username', 'displayname']))

        # Deadlines
        self.assertEquals(len(content[0]['deadlines']), 1)
        deadline = content[0]['deadlines'][0]
        self.assertEquals(set(deadline.keys()),
                          set(['id', 'deadline']))

        # Tags
        self.assertEquals(len(content[0]['tags']), 2)
        tag = content[0]['tags'][0]
        self.assertEquals(set(tag.keys()),
                          set(['id', 'tag']))


    def test_list(self):
        self._test_list_as('a1admin')

    def test_list_as_superuser(self):
        self.testhelper.create_superuser('superuser')
        self._test_list_as('superuser')


class GroupManagerTestMixin(object):
    def create_examinerdict(self, id=None, username=None):
        dct = {'id': id}
        if username:
            dct['user'] = {'id': getattr(self.testhelper, username).id}
        return dct

    def create_candidatedict(self, id=None, username=None, candidate_id=None):
        dct = {'id': id}
        dct['candidate_id'] = candidate_id
        if username:
            dct['user'] = {'id': getattr(self.testhelper, username).id}
        return dct

    def create_tagdict(self, tag):
        return {'tag': tag}



class TestGroupManager(TestCase, GroupManagerTestMixin):
    def setUp(self):
        self.client = RestClient()
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                       subjects=['sub'],
                       periods=['p1'],
                       assignments=['a1'])
        self.a1 = self.testhelper.sub_p1_a1
        self.testhelper.create_user('user1')
        self.testhelper.create_user('user2')
        self.testhelper.create_user('user3')
        self.testhelper.create_user('notusedforanything') # NOTE: GroupManager requires a user for very few actions. The tests that do not use these actions use this user.

    def test_update_group(self):
        self.assertEquals(AssignmentGroup.objects.all().count(), 0)
        manager = GroupManager(self.testhelper.notusedforanything, self.a1)
        self.assertEquals(manager.group.id, None)
        manager.update_group(name='Nametest', is_open=False)
        self.assertIsNotNone(manager.group.id)
        self.assertEquals(manager.group.name, 'Nametest')
        self.assertEquals(manager.group.is_open, False)
        self.assertEquals(AssignmentGroup.objects.all().count(), 1)

    def test_create_first_deadline_not_available(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1')
        manager = GroupManager(self.testhelper.notusedforanything, group=self.testhelper.sub_p1_a1_g1)
        self.assertEquals(manager.group.id, self.testhelper.sub_p1_a1_g1.id)
        manager.create_first_deadline_if_available()
        self.assertEquals(manager.group.deadlines.count(), 0)

    def test_create_first_deadline(self):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1')
        g1 = self.testhelper.sub_p1_a1_g1
        g1.parentnode.first_deadline = datetime(2005, 1, 1)
        g1.parentnode.save()
        manager = GroupManager(self.testhelper.notusedforanything, group=g1)
        self.assertEquals(manager.group.id, self.testhelper.sub_p1_a1_g1.id)
        manager.create_first_deadline_if_available()
        self.assertEquals(manager.group.deadlines.count(), 1)
        self.assertEquals(manager.group.deadlines.all()[0].deadline, datetime(2005, 1, 1))

    #
    # Examiners
    #

    def test_update_examiners_create(self):
        manager = GroupManager(self.testhelper.notusedforanything, self.a1)
        manager.group.save()
        manager.update_examiners([self.create_examinerdict(username='user1')])
        examiners = manager.get_group_from_db().examiners.all()
        self.assertEquals(len(examiners), 1)
        created = examiners[0]
        self.assertEquals(created.user.id, self.testhelper.user1.id)

        manager.update_examiners([self.create_examinerdict(id=created.id),
                                  self.create_examinerdict(username='user2')])
        examiners = manager.get_group_from_db().examiners.all()
        self.assertEquals(len(examiners), 2)
        ids = [examiner.id for examiner in examiners]
        self.assertEquals(set(ids),
                          set([self.testhelper.user1.id, self.testhelper.user2.id]))

    def test_update_examiners_create_duplicate(self):
        manager = GroupManager(self.testhelper.notusedforanything, self.a1)
        manager.group.save()
        manager.group.examiners.create(user=self.testhelper.user1)
        with self.assertRaises(ValidationError):
            manager.update_examiners([self.create_examinerdict(username='user1')])

    def test_update_examiners_delete(self):
        manager = GroupManager(self.testhelper.notusedforanything, self.a1)
        manager.group.save()
        manager.group.examiners.create(user=self.testhelper.user1)
        manager.group.examiners.create(user=self.testhelper.user2)
        manager.update_examiners([])
        examiners = manager.get_group_from_db().examiners.all()
        self.assertEquals(len(examiners), 0)

    def test_update_examiners_complex(self):
        manager = GroupManager(self.testhelper.notusedforanything, self.a1)
        manager.group.save()
        manager.group.examiners.create(user=self.testhelper.user1)
        manager.group.examiners.create(user=self.testhelper.user2)
        manager.update_examiners([self.create_examinerdict(id=self.testhelper.user1.id), # keep user1
                                  # ... delete user2
                                  self.create_examinerdict(username='user3')]) # create user3
        examiners = manager.get_group_from_db().examiners.all()
        self.assertEquals(len(examiners), 2)
        ids = [examiner.id for examiner in examiners]
        self.assertEquals(set(ids),
                          set([self.testhelper.user1.id, self.testhelper.user3.id]))


    #
    # Candidates
    #

    def test_update_candidates_create(self):
        manager = GroupManager(self.testhelper.notusedforanything, self.a1)
        manager.group.save()
        manager.update_candidates([self.create_candidatedict(username='user1')])
        candidates = manager.get_group_from_db().candidates.all()
        self.assertEquals(len(candidates), 1)
        created = candidates[0]
        self.assertEquals(created.student.id, self.testhelper.user1.id)
        self.assertEquals(created.candidate_id, None)

        manager.update_candidates([self.create_candidatedict(id=created.id),
                                   self.create_candidatedict(username='user2')])
        candidates = manager.get_group_from_db().candidates.all()
        self.assertEquals(len(candidates), 2)
        ids = [candidate.id for candidate in candidates]
        self.assertEquals(set(ids),
                          set([self.testhelper.user1.id, self.testhelper.user2.id]))

    def test_update_candidates_create_candidate_id(self):
        manager = GroupManager(self.testhelper.notusedforanything, self.a1)
        manager.group.save()
        manager.update_candidates([self.create_candidatedict(username='user1',
                                                             candidate_id='secret')])
        candidates = manager.get_group_from_db().candidates.all()
        created = candidates[0]
        self.assertEquals(created.candidate_id, 'secret')

    def test_update_candidates_create_duplicate_allowed(self):
        manager = GroupManager(self.testhelper.notusedforanything, self.a1)
        manager.group.save()
        created = manager.group.candidates.create(student=self.testhelper.user1)
        # Does not raise exception, event if they are the same user
        manager.update_candidates([self.create_candidatedict(id=created.id,
                                                             candidate_id=created.candidate_id,
                                                             username='user1'),
                                   self.create_candidatedict(username='user1')])

    def test_update_candidates_delete(self):
        superuser = self.testhelper.create_superuser('superuser')
        manager = GroupManager(superuser, self.a1)
        manager.group.save()
        manager.group.candidates.create(student=self.testhelper.user1)
        manager.group.candidates.create(student=self.testhelper.user2)
        manager.update_candidates([])
        candidates = manager.get_group_from_db().candidates.all()
        self.assertEquals(len(candidates), 0)

    def test_update_candidates_delete_as_nobody(self):
        nobody = self.testhelper.create_user('nobody')
        manager = GroupManager(nobody, self.a1)
        manager.group.save()
        manager.group.candidates.create(student=self.testhelper.user1)
        manager.group.candidates.create(student=self.testhelper.user2)
        with self.assertRaises(PermissionDeniedError):
            manager.update_candidates([])

    def test_update_candidates_complex(self):
        superuser = self.testhelper.create_superuser('superuser')
        manager = GroupManager(superuser, self.a1)
        manager.group.save()
        manager.group.candidates.create(student=self.testhelper.user1)
        manager.group.candidates.create(student=self.testhelper.user2)
        manager.update_candidates([self.create_candidatedict(id=self.testhelper.user1.id), # keep user1
                                  # ... delete user2
                                  self.create_candidatedict(username='user3')]) # create user3
        candidates = manager.get_group_from_db().candidates.all()
        self.assertEquals(len(candidates), 2)
        ids = [candidate.id for candidate in candidates]
        self.assertEquals(set(ids),
                          set([self.testhelper.user1.id, self.testhelper.user3.id]))

    #
    # Tags
    #

    def test_update_tags(self):
        manager = GroupManager(self.testhelper.notusedforanything, self.a1)
        manager.group.save()
        manager.update_tags([self.create_tagdict('mytag')])
        tags = manager.get_group_from_db().tags.all()
        self.assertEquals(len(tags), 1)
        created = tags[0]
        self.assertEquals(created.tag, 'mytag')

        manager.update_tags([self.create_tagdict('tag1'),
                             self.create_tagdict('tag2')])
        tagsObjs = manager.get_group_from_db().tags.all()
        self.assertEquals(len(tagsObjs), 2)
        tags = [tagObj.tag for tagObj in tagsObjs]
        self.assertEquals(set(tags), set(['tag1', 'tag2']))



class TestGroupRest(TestCase, GroupManagerTestMixin):
    def setUp(self):
        self.testhelper = TestHelper()
        self.testhelper.add(nodes='uni',
                            subjects=['sub'],
                            periods=['p1'],
                            assignments=['a1:admin(a1admin)'])
        self.client = RestClient()
        self.testhelper.create_user('candidate1')
        self.testhelper.create_user('examiner1')
        self.testhelper.create_superuser('grandma')
        self.a1id = self.testhelper.sub_p1_a1.id

    def _geturl(self, assignment_id, querystringParams=None):
        url = '/devilry_subjectadmin/rest/group/{0}/'.format(assignment_id)
        if querystringParams:
            url = '{}?{}'.format(url, urlencode(querystringParams))
        return url

    def _postas(self, username, assignment_id, data={}):
        self.client.login(username=username, password='test')
        return self.client.rest_post(self._geturl(assignment_id), data)

    def test_create_minimal(self):
        data = [{'name': 'g1',
                 'is_open': False}]
        content, response = self._postas('a1admin', self.a1id, data)
        self.assertEquals(response.status_code, 201)
        self.assertEquals(len(content), 1)
        first = content[0]
        self.assertEquals(set(first.keys()),
                          set(['name', 'id', 'etag', 'status', 'is_open', 'parentnode',
                               'feedback', 'deadlines', 'candidates', 'tags',
                               'examiners', 'num_deliveries']))
        self.assertEquals(first['name'], 'g1')
        self.assertEquals(first['is_open'], False)
        self.assertEquals(first['parentnode'], self.a1id)
        self.assertEquals(first['num_deliveries'], 0)
        self.assertEquals(first['feedback'], None)
        self.assertEquals(first['deadlines'], [])
        self.assertEquals(first['candidates'], [])
        self.assertEquals(first['examiners'], [])
        self.assertEquals(first['tags'], [])

        groups = self.testhelper.sub_p1_a1.assignmentgroups.all()
        self.assertEquals(len(groups), 1)
        self.assertEquals(first['id'], groups[0].id)


    def _test_create_as(self, username):
        a1 = self.testhelper.sub_p1_a1
        a1.first_deadline = datetime(2005, 1, 1)
        a1.save()
        data = [{'name': 'g1',
                 'is_open': False,
                 'examiners': [self.create_examinerdict(username='examiner1')],
                 'candidates': [self.create_candidatedict(username='candidate1')],
                 'tags': [self.create_tagdict('mytag')]}]
        content, response = self._postas(username, self.a1id, data)
        #from pprint import pprint
        #print 'Response content:'
        #pprint(content)
        self.assertEquals(response.status_code, 201)
        self.assertEquals(len(content), 1)
        first = content[0]

        self.assertEquals(first['name'], 'g1')
        self.assertEquals(first['is_open'], True) # NOTE: Overrides the parameter since first_deadline is set.
        self.assertEquals(first['parentnode'], self.a1id)
        self.assertEquals(first['num_deliveries'], 0)

        # Feedback
        self.assertEquals(first['feedback'], None)

        # Deadlines
        self.assertEquals(len(first['deadlines']), 1)
        self.assertEquals(first['deadlines'][0]['deadline'], '2005-01-01T00:00:00')
        self.assertEquals(set(first['deadlines'][0].keys()), set(['id', 'deadline']))

        # Tags
        self.assertEquals(len(first['tags']), 1)
        tag = first['tags'][0]
        self.assertEquals(tag['tag'], 'mytag')
        self.assertEquals(set(tag.keys()), set(['id', 'tag']))

        # Examiners
        self.assertEquals(len(first['examiners']), 1)
        examiner = first['examiners'][0]
        self.assertEquals(set(examiner.keys()),
                          set(['id', 'user']))
        self.assertEquals(set(examiner['user'].keys()),
                          set(['email', 'full_name', 'id', 'username', 'displayname']))
        self.assertEquals(examiner['user']['id'], self.testhelper.examiner1.id)
        self.assertEquals(examiner['user']['username'], 'examiner1')

        # Candidates
        self.assertEquals(len(first['candidates']), 1)
        candidate = first['candidates'][0]
        self.assertEquals(set(candidate.keys()),
                          set(['id', 'user', 'candidate_id']))
        self.assertEquals(set(candidate['user'].keys()),
                          set(['email', 'full_name', 'id', 'username', 'displayname']))
        self.assertEquals(candidate['user']['id'], self.testhelper.candidate1.id)
        self.assertEquals(candidate['candidate_id'], '')
        self.assertEquals(candidate['user']['username'], 'candidate1')

        # It was actually created?
        groups = self.testhelper.sub_p1_a1.assignmentgroups.all()
        self.assertEquals(len(groups), 1)
        self.assertEquals(first['id'], groups[0].id)

    def test_create_as_assignmentadmin(self):
        self._test_create_as('a1admin')

    def test_create_as_superuser(self):
        self._test_create_as('grandma')

    def test_noperm(self):
        self.testhelper.create_user('nobody')
        data = [{'name': 'g1',
                 'is_open': False}]
        content, response = self._postas('nobody', self.a1id, data)
        self.assertEquals(response.status_code, 403)
        self.assertEquals(content, {u'detail': u'Permission denied'})

    def test_create_ro_fields(self):
        data = [{'name': 'g1',
                 'is_open': False,
                 'id': None,
                 'feedback': 'should be ignored',
                 'num_deliveries': 'should be ignored',
                 'deadlines': 'should be ignored'}]
        content, response = self._postas('a1admin', self.a1id, data)
        self.assertEquals(response.status_code, 201)


    #
    #
    # PUT
    #
    #
    def _putas(self, username, assignment_id, data={}, querystringParams={}):
        self.client.login(username=username, password='test')
        return self.client.rest_put(self._geturl(assignment_id, querystringParams), data)

    def _add_group(self, name, candidates, examiners):
        self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate({candidates}):examiner({examiners})'.format(**vars()))
        return getattr(self.testhelper, 'sub_p1_a1_' + name)

    def test_put_minimal(self):
        group = self._add_group('g1', candidates='candidate1', examiners='examiner1')
        self.assertEquals(group.name, 'g1')
        self.assertEquals(group.is_open, True)
        data = [{'id': group.id,
                 'name': 'changed',
                 'is_open': False}]
        content, response = self._putas('a1admin', self.a1id, data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        first = content[0]

        self.assertEquals(set(first.keys()),
                          set(['name', 'id', 'etag', 'status', 'is_open', 'parentnode',
                               'feedback', 'deadlines', 'candidates', 'tags',
                               'examiners', 'num_deliveries']))
        self.assertEquals(first['name'], 'changed')
        self.assertEquals(first['is_open'], False)
        self.assertEquals(first['parentnode'], self.a1id)
        self.assertEquals(first['num_deliveries'], 0)
        self.assertEquals(first['feedback'], None)
        self.assertEquals(first['deadlines'], [])
        self.assertEquals(first['candidates'], [])
        self.assertEquals(first['examiners'], [])
        self.assertEquals(first['tags'], [])

        groups = self.testhelper.sub_p1_a1.assignmentgroups.all()
        self.assertEquals(len(groups), 1)
        self.assertEquals(first['id'], groups[0].id)

    def _test_put_as(self, username):
        group = self._add_group('g1', candidates='candidate2', examiners='examiner2')
        data = [{'id': group.id,
                 'name': 'changed',
                 'is_open': False,
                 'examiners': [self.create_examinerdict(username='examiner1')],
                 'candidates': [self.create_candidatedict(username='candidate1')],
                 'tags': [self.create_tagdict('mytag')]}]
        content, response = self._putas(username, self.a1id, data)
        #from pprint import pprint
        #print 'Response content:'
        #pprint(content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        first = content[0]

        self.assertEquals(first['name'], 'changed')
        self.assertEquals(first['is_open'], False)
        self.assertEquals(first['parentnode'], self.a1id)
        self.assertEquals(first['num_deliveries'], 0)

        # Feedback
        self.assertEquals(first['feedback'], None)

        # Deadlines
        self.assertEquals(first['deadlines'], [])

        # Tags
        self.assertEquals(len(first['tags']), 1)
        tag = first['tags'][0]
        self.assertEquals(tag['tag'], 'mytag')
        self.assertEquals(set(tag.keys()), set(['id', 'tag']))

        # Examiners
        self.assertEquals(len(first['examiners']), 1)
        examiner = first['examiners'][0]
        self.assertEquals(set(examiner.keys()),
                          set(['id', 'user']))
        self.assertEquals(set(examiner['user'].keys()),
                          set(['email', 'full_name', 'id', 'username', 'displayname']))
        self.assertEquals(examiner['user']['id'], self.testhelper.examiner1.id)
        self.assertEquals(examiner['user']['username'], 'examiner1')

        # Candidates
        self.assertEquals(len(first['candidates']), 1)
        candidate = first['candidates'][0]
        self.assertEquals(set(candidate.keys()),
                          set(['id', 'user', 'candidate_id']))
        self.assertEquals(set(candidate['user'].keys()),
                          set(['email', 'full_name', 'id', 'username', 'displayname']))
        self.assertEquals(candidate['user']['id'], self.testhelper.candidate1.id)
        self.assertEquals(candidate['candidate_id'], '')
        self.assertEquals(candidate['user']['username'], 'candidate1')

        # It was actually updated?
        group = self.testhelper.sub_p1_a1.assignmentgroups.get(id=group.id)
        self.assertEquals(group.name, 'changed')

    def test_put_as_superuser(self):
        self.testhelper.create_superuser('superuser')
        self._test_put_as('superuser')

    def test_put_as_assignmentadmin(self):
        self._test_put_as('a1admin')

    def test_put_doesnotexist(self):
        data = [{'id': 100000,
                 'name': 'changed',
                 'is_open': False}]
        content, response = self._putas('grandma', 10000, data)
        self.assertEquals(response.status_code, 404)

    def test_put_denied(self):
        self.testhelper.create_user('nobody')
        self.testhelper.add_to_path('uni;sub.p1.a1.g1')
        group = self.testhelper.sub_p1_a1_g1
        data = [{'name': 'changed',
                 'is_open': False}]
        content, response = self._putas('nobody', self.a1id, data)
        self.assertEquals(response.status_code, 403)

    def test_put_ro_fields(self):
        group = self._add_group('g1', candidates='candidate1', examiners='examiner1')
        self.assertEquals(group.name, 'g1')
        self.assertEquals(group.is_open, True)
        data = [{'id': group.id,
                 'name': 'changed',
                 'is_open': False,
                 'feedback': 'should be ignored',
                 'num_deliveries': 'should be ignored',
                 'deadlines': 'should be ignored'}]
        content, response = self._putas('a1admin', self.a1id, data)
        self.assertEquals(response.status_code, 200)

    def test_put_examinersonly(self):
        group = self._add_group('g1', candidates='candidate2', examiners='examiner2')
        self.assertEquals(group.name, 'g1')
        self.assertEquals(group.is_open, True)
        data = [{'id': group.id,
                 'name': 'changed',
                 'is_open': False,
                 'examiners': [self.create_examinerdict(username='examiner1')],
                 'candidates': [self.create_candidatedict(username='candidate1')],
                 'tags': [self.create_tagdict('mytag')]}]
        content, response = self._putas('a1admin', self.a1id, data, {
            'examinersOnly': 'true'
        })
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        first = content[0]

        self.assertEquals(first['name'], 'g1') #Unchanged
        self.assertEquals(first['is_open'], True) #Unchanged

        # Tags (unchanged)
        self.assertEquals(len(first['tags']), 0)

        # Examiners (changed)
        self.assertEquals(len(first['examiners']), 1)
        examiner = first['examiners'][0]
        self.assertEquals(examiner['user']['id'], self.testhelper.examiner1.id)

        ## Candidates (unchanged)
        self.assertEquals(len(first['candidates']), 1)
        candidate = first['candidates'][0]
        self.assertEquals(candidate['user']['id'], self.testhelper.candidate2.id)


    def test_put_tagsonly(self):
        group = self._add_group('g1', candidates='candidate2', examiners='examiner2')
        self.assertEquals(group.name, 'g1')
        self.assertEquals(group.is_open, True)
        data = [{'id': group.id,
                 'name': 'changed',
                 'is_open': False,
                 'examiners': [self.create_examinerdict(username='examiner1')],
                 'candidates': [self.create_candidatedict(username='candidate1')],
                 'tags': [self.create_tagdict('mytag')]}]
        content, response = self._putas('a1admin', self.a1id, data, {
            'tagsOnly': 'true'
        })
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(content), 1)
        first = content[0]

        self.assertEquals(first['name'], 'g1') #Unchanged
        self.assertEquals(first['is_open'], True) #Unchanged

        # Tags (changed)
        self.assertEquals(len(first['tags']), 1)
        tag = first['tags'][0]
        self.assertEquals(tag['tag'], 'mytag')

        # Examiners (unchanged)
        self.assertEquals(len(first['examiners']), 1)
        examiner = first['examiners'][0]
        self.assertEquals(examiner['user']['id'], self.testhelper.examiner2.id)

        ## Candidates (unchanged)
        self.assertEquals(len(first['candidates']), 1)
        candidate = first['candidates'][0]
        self.assertEquals(candidate['user']['id'], self.testhelper.candidate2.id)


    #
    #
    # DELETE
    #
    #

    def _add_group_with_delivery(self, name, **kwargs):
        group = self._add_group(name, **kwargs)
        self.testhelper.add_to_path('uni;sub.p1.a1.{0}.d1'.format(name))
        self.testhelper.add_delivery(group)
        return group

    def _deleteas(self, username, assignment_id, data):
        self.client.login(username=username, password='test')
        return self.client.rest_put(self._geturl(assignment_id), data,
                                    X_DEVILRY_DELETEHACK='1')

    def _test_delete_ok_as(self, group, username):
        data = [{'id': group.id}]
        content, response = self._deleteas(username, self.a1id, data)
        self.assertEquals(response.status_code, 204)
        self.assertEquals(content, None)
        self.assertFalse(AssignmentGroup.objects.filter(id=group.id).exists())

    def test_delete_as_superuser(self):
        self.testhelper.create_superuser('superuser')
        group = self._add_group('g1', candidates='candidate2', examiners='examiner2')
        self._test_delete_ok_as(group, 'superuser')


    def test_delete_as_a1admin(self):
        group = self._add_group('g1', candidates='candidate2', examiners='examiner2')
        self._test_delete_ok_as(group, 'a1admin')


    def _test_delete_noperm_as(self, group, username):
        data = [{'id': group.id}]
        content, response = self._deleteas(username, self.a1id, data)
        #from pprint import pprint
        #print 'Response content:'
        #pprint(content)
        self.assertEquals(response.status_code, 403)
        self.assertTrue(AssignmentGroup.objects.filter(id=group.id).exists())

    def test_delete_with_content_as_superuser(self):
        self.testhelper.create_superuser('superuser')
        group = self._add_group_with_delivery('g1',
                                              candidates='candidate2',
                                              examiners='examiner2')
        self._test_delete_ok_as(group, 'superuser')

    def test_delete_with_content_as_a1admin(self):
        group = self._add_group_with_delivery('g1',
                                              candidates='candidate2',
                                              examiners='examiner2')
        self._test_delete_noperm_as(group, 'a1admin')



#class TestInstanceGroupRest(TestCase, GroupManagerTestMixin):
    #def setUp(self):
        #self.testhelper = TestHelper()
        #self.testhelper.add(nodes='uni',
                            #subjects=['sub'],
                            #periods=['p1'],
                            #assignments=['a1:admin(a1admin)'])
        #self.client = RestClient()
        #self.testhelper.create_superuser('grandma')
        #self.testhelper.create_user('candidate1')
        #self.testhelper.create_user('examiner1')
        #self.testhelper.create_superuser('superuser')
        #self.a1id = self.testhelper.sub_p1_a1.id

    #def _geturl(self, assignment_id, group_id):
        #return '/devilry_subjectadmin/rest/group/{0}/{1}'.format(assignment_id, group_id)

    #def _putas(self, username, assignment_id, group_id, data={}):
        #self.client.login(username=username, password='test')
        #return self.client.rest_put(self._geturl(assignment_id, group_id), data)

    #def _add_group(self, name, candidates, examiners):
        #self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate({candidates}):examiner({examiners})'.format(**vars()))
        #return getattr(self.testhelper, 'sub_p1_a1_' + name)

    #def test_put_minimal(self):
        #group = self._add_group('g1', candidates='candidate1', examiners='examiner1')
        #self.assertEquals(group.name, 'g1')
        #self.assertEquals(group.is_open, True)
        #data = {'name': 'changed',
                #'is_open': False}
        #content, response = self._putas('a1admin', self.a1id, group.id, data)
        #self.assertEquals(response.status_code, 200)
        #self.assertEquals(set(content.keys()),
                          #set(['name', 'id', 'etag', 'status', 'is_open', 'parentnode',
                               #'feedback', 'deadlines', 'candidates', 'tags',
                               #'examiners', 'num_deliveries']))
        #self.assertEquals(content['name'], 'changed')
        #self.assertEquals(content['is_open'], False)
        #self.assertEquals(content['parentnode'], self.a1id)
        #self.assertEquals(content['num_deliveries'], 0)
        #self.assertEquals(content['feedback'], None)
        #self.assertEquals(content['deadlines'], [])
        #self.assertEquals(content['candidates'], [])
        #self.assertEquals(content['examiners'], [])
        #self.assertEquals(content['tags'], [])

        #groups = self.testhelper.sub_p1_a1.assignmentgroups.all()
        #self.assertEquals(len(groups), 1)
        #self.assertEquals(content['id'], groups[0].id)

    #def _test_put_as(self, username):
        #group = self._add_group('g1', candidates='candidate2', examiners='examiner2')
        #data = {'name': 'changed',
                #'is_open': False,
                #'examiners': [self.create_examinerdict(username='examiner1')],
                #'candidates': [self.create_candidatedict(username='candidate1')],
                #'tags': [self.create_tagdict('mytag')]}
        #content, response = self._putas(username, self.a1id, group.id, data)
        ##from pprint import pprint
        ##print 'Response content:'
        ##pprint(content)
        #self.assertEquals(response.status_code, 200)

        #self.assertEquals(content['name'], 'changed')
        #self.assertEquals(content['is_open'], False)
        #self.assertEquals(content['parentnode'], self.a1id)
        #self.assertEquals(content['num_deliveries'], 0)

        ## Feedback
        #self.assertEquals(content['feedback'], None)

        ## Deadlines
        #self.assertEquals(content['deadlines'], [])

        ## Tags
        #self.assertEquals(len(content['tags']), 1)
        #tag = content['tags'][0]
        #self.assertEquals(tag['tag'], 'mytag')
        #self.assertEquals(set(tag.keys()), set(['id', 'tag']))

        ## Examiners
        #self.assertEquals(len(content['examiners']), 1)
        #examiner = content['examiners'][0]
        #self.assertEquals(set(examiner.keys()),
                          #set(['id', 'user']))
        #self.assertEquals(set(examiner['user'].keys()),
                          #set(['email', 'full_name', 'id', 'username']))
        #self.assertEquals(examiner['user']['id'], self.testhelper.examiner1.id)
        #self.assertEquals(examiner['user']['username'], 'examiner1')

        ## Candidates
        #self.assertEquals(len(content['candidates']), 1)
        #candidate = content['candidates'][0]
        #self.assertEquals(set(candidate.keys()),
                          #set(['id', 'user', 'candidate_id']))
        #self.assertEquals(set(candidate['user'].keys()),
                          #set(['email', 'full_name', 'id', 'username']))
        #self.assertEquals(candidate['user']['id'], self.testhelper.candidate1.id)
        #self.assertEquals(candidate['candidate_id'], '')
        #self.assertEquals(candidate['user']['username'], 'candidate1')

        ## It was actually updated?
        #group = self.testhelper.sub_p1_a1.assignmentgroups.get(id=group.id)
        #self.assertEquals(group.name, 'changed')

    #def test_put_as_superuser(self):
        #self._test_put_as('superuser')

    #def test_put_as_assignmentadmin(self):
        #self._test_put_as('a1admin')

    #def test_put_doesnotexist(self):
        #data = {'name': 'changed',
                #'is_open': False}
        #content, response = self._putas('grandma', 10000, 100000, data)
        #self.assertEquals(response.status_code, 404)

    #def test_put_denied(self):
        #self.testhelper.create_user('nobody')
        #self.testhelper.add_to_path('uni;sub.p1.a1.g1')
        #group = self.testhelper.sub_p1_a1_g1
        #data = {'name': 'changed',
                #'is_open': False}
        #content, response = self._putas('nobody', self.a1id, group.id, data)
        #self.assertEquals(response.status_code, 403)

    #def test_put_ro_fields(self):
        #group = self._add_group('g1', candidates='candidate1', examiners='examiner1')
        #self.assertEquals(group.name, 'g1')
        #self.assertEquals(group.is_open, True)
        #data = {'name': 'changed',
                #'is_open': False,
                #'feedback': 'should be ignored',
                #'id': 'should be ignored',
                #'num_deliveries': 'should be ignored',
                #'deadlines': 'should be ignored'}
        #content, response = self._putas('a1admin', self.a1id, group.id, data)
        #self.assertEquals(response.status_code, 200)




    ##
    ## GET
    ##
    #def _getas(self, username, assignment_id, group_id):
        #self.client.login(username=username, password='test')
        #return self.client.rest_get(self._geturl(assignment_id, group_id))

    #def _test_get_as(self, username):
        #self.testhelper.add_to_path('uni;sub.p1.a1.g1:candidate(candidate1):examiner(examiner1).d1:ends(5)')
        #self.testhelper.add_to_path('uni;sub.p1.a1.g1.d2:ends(10)')
        #group = self.testhelper.sub_p1_a1_g1
        #content, response = self._getas(username, self.a1id, group.id)
        ##from pprint import pprint
        ##print 'Response content:'
        ##pprint(content)
        #self.assertEquals(response.status_code, 200)
        #self.assertEquals(set(content.keys()),
                          #set(['name', 'id', 'etag', 'status', 'is_open', 'parentnode',
                               #'feedback', 'deadlines', 'candidates', 'tags',
                               #'examiners', 'num_deliveries']))
        #self.assertEquals(content['name'], 'g1')
        #self.assertEquals(content['is_open'], True)
        #self.assertEquals(content['parentnode'], self.a1id)
        #self.assertEquals(content['num_deliveries'], 0)
        #self.assertEquals(content['feedback'], None)

        ## Deadlines
        #self.assertEquals(len(content['deadlines']), 2)
        #self.assertEquals(set(content['deadlines'][0].keys()),
                          #set(['id', 'deadline']))

        ## Candidates
        #self.assertEquals(len(content['candidates']), 1)
        #candidate = content['candidates'][0]
        #self.assertEquals(candidate['candidate_id'], None)
        #self.assertEquals(candidate['user'], {'id': self.testhelper.candidate1.id,
                                              #'username': 'candidate1',
                                              #'email': 'candidate1@example.com',
                                              #'full_name': None})

        ## Examiners
        #self.assertEquals(len(content['examiners']), 1)
        #examiner = content['examiners'][0]
        #self.assertEquals(examiner['user'], {'id': self.testhelper.examiner1.id,
                                              #'username': 'examiner1',
                                              #'email': 'examiner1@example.com',
                                              #'full_name': None})

    #def test_get_as_assignmentadmin(self):
        #self._test_get_as('a1admin')

    #def test_get_as_superuser(self):
        #self._test_get_as('superuser')

    #def test_get_denied(self):
        #self.testhelper.create_user('nobody')
        #self.testhelper.add_to_path('uni;sub.p1.a1.g1')
        #group = self.testhelper.sub_p1_a1_g1
        #content, response = self._getas('nobody', self.a1id, group.id)
        #self.assertEquals(response.status_code, 403)
