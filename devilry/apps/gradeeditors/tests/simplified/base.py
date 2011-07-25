from devilry.apps.core import testhelper
from devilry.simplified import PermissionDenied
from devilry.apps.gradeeditors.models import FeedbackDraft


class SimplifiedFeedbackDraftTestBase(testhelper.TestHelper):
    # The SimplifiedFeedbackDraft (from examiner of administrator)
    #SimplifiedFeedbackDraft = ....

    def setUp(self):
        self.create_superuser('superuser')
        self.add(nodes='uni',
                 subjects=['inf101'],
                 periods=['spring01'],
                 assignments=['assignment1:admin(goodadmin)', 'assignment2:admin(badadmin)'])
        self.add_to_path('uni;inf101.spring01.assignment1.group1:candidate(firststudent):examiner(goodexaminer)')
        self.add_to_path('uni;inf101.spring01.assignment1.group2:candidate(secondstudent):examiner(badexaminer)')
        group = self.inf101_spring01_assignment1_group1
        self.delivery = self.add_delivery(group)
        self._setup_users()

    def _create_draft_without_simplified(self):
        return FeedbackDraft.objects.create(delivery=self.delivery,
                                            draft='tst',
                                            saved_by=self.goodexaminer)

    #def _setup_users(self):
        #
        #Setup:
        #    self.gooduser = #  A user that HAS permissions on FeedbackDraft for self.delivery
        #    self.baduser = # A user that does NOT have permissions on FeedbackDraft for self.delivery




class SimplifiedFeedbackDraftCreateTestBase(SimplifiedFeedbackDraftTestBase):
    def _create_success_test(self, user):
        id = self.SimplifiedFeedbackDraft.create(user,
                                                 delivery=self.delivery,
                                                 draft='tst')
        FeedbackDraft.objects.get(id=id) # Will fail if it does not exist

    def test_create_as_gooduser(self):
        self._create_success_test(self.gooduser)

    #def test_create_as_superuser(self):
        #self._create_success_test(self.superuser)

    def test_create_as_baduser(self):
        with self.assertRaises(PermissionDenied):
            self.SimplifiedFeedbackDraft.create(self.baduser,
                                                         delivery=self.delivery,
                                                         draft='tst')

class SimplifiedFeedbackDraftReadTestBase(SimplifiedFeedbackDraftTestBase):

    def _read_success_test(self, user):
        draft = self._create_draft_without_simplified()
        result = self.SimplifiedFeedbackDraft.read(user, draft.id)
        self.assertEquals(result, {'delivery': 1,
                                   'saved_by': 5,
                                   'shared': False,
                                   'draft': u'tst',
                                   'id': 1})

    def test_read_as_gooduser(self):
        self._read_success_test(self.gooduser)

    #def test_read_as_superuser(self):
        #self._read_success_test(self.superuser)

    def test_read_as_baduser(self):
        draft = self._create_draft_without_simplified()
        with self.assertRaises(PermissionDenied):
            self.SimplifiedFeedbackDraft.read(self.baduser, draft.id)


class SimplifiedFeedbackDraftUpdateTestBase(SimplifiedFeedbackDraftTestBase):
    def _update_success_test(self, user):
        draft = self._create_draft_without_simplified()
        self.SimplifiedFeedbackDraft.update(user, draft.id,
                                            delivery=self.delivery,
                                            draft='UPDATED')
        updated = FeedbackDraft.objects.get(id=draft.id)
        self.assertEquals(updated.draft, 'UPDATED')

    def test_update_as_gooduser(self):
        self._update_success_test(self.gooduser)

    def test_update_as_baduser(self):
        draft = self._create_draft_without_simplified()
        with self.assertRaises(PermissionDenied):
            self.SimplifiedFeedbackDraft.update(self.baduser, draft.id,
                                                delivery=self.delivery,
                                                draft='tst')
