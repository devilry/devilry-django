from django.test import TestCase
from django.contrib.auth.models import User

from devilry.devilry_rest.testclient import RestClient
from devilry.apps.core.testhelper import TestHelper



class TestSearchForUsers(TestCase):
    def setUp(self):
        self.client = RestClient()
        for username, fullname in [('baldr', 'God of Beauty'),
                                   ('freyja', 'Goddess of Love'),
                                   ('freyr', 'God of Fertility'),
                                   ('kvasir', 'God of Inspiration'),
                                   ('loki', 'Trickster and god of Mischief'),
                                   ('thor', 'God of thunder and Battle'),
                                   ('odin', 'The "All Father"')]:
            user = User.objects.create(username=username,
                                       email='{0}@{1}.com'.format(fullname.lower().replace(' ', '.'),
                                                                  username))
            user.devilryuserprofile.full_name = fullname
            user.devilryuserprofile.save()

        self.testhelper = TestHelper()
        self.testhelper.add(nodes="uni:admin(uniadmin)",
                            subjects=["sub:admin(subadmin)"],
                            periods=["p1:admin(p1admin)"],
                            assignments=["a1:admin(a1admin)"])
        self.url = '/devilry_usersearch/search'


    def _listas(self, username, **data):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url, **data)

    def _searchas(self, username, query):
        return self._listas(username, query=query)[0]

    def _test_search_as(self, username):
        content, response = self._listas(username, query='')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(self._searchas(username, 'fre')), 2)
        self.assertEquals(len(self._searchas(username, 'fr')), 0)
        self.assertEquals(len(self._searchas(username, 'f')), 0)
        self.assertEquals(len(self._searchas(username, 'GOD')), 6)
        self.assertEquals(len(self._searchas(username, 'god')), 6)
        self.assertEquals(len(self._searchas(username, 'thor')), 1)
        self.assertEquals(len(self._searchas(username, 'tHoR')), 1)
        thor = self._searchas(username, 'tHoR')[0]
        self.assertEquals(thor,
                          {u'username': u'thor',
                           u'id': User.objects.get(username='thor').id,
                           u'full_name': u'God of thunder and Battle',
                           u'languagecode': None,
                           u'email': u'god.of.thunder.and.battle@thor.com'})

    def test_search_nodeadmin(self):
        self._test_search_as('uniadmin')

    def test_search_subjectadmin(self):
        self._test_search_as('subadmin')

    def test_search_periodadmin(self):
        self._test_search_as('p1admin')

    def test_search_assignmentadmin(self):
        self._test_search_as('a1admin')

    def test_search_superadmin(self):
        self.testhelper.create_superuser('grandma')
        self._test_search_as('grandma')

    def test_search_nobody(self):
        self.testhelper.create_user('nobody')
        content, response = self._listas('nobody', query='')
        self.assertEquals(response.status_code, 403)

    def test_search_limit(self):
        for index in xrange(15):
            username = 'student{0}'.format(index)
            user = User.objects.create(username=username,
                                       email='{0}@example.com'.format(username))
        self.assertEquals(len(self._searchas('uniadmin', 'student')), 10)
