from django.core.exceptions import ValidationError

from devilry.apps.core import testhelper
from devilry.simplified import PermissionDenied
from devilry.apps.gradeeditors.models import FeedbackDraft, Config
from devilry.apps.core import pluginloader


pluginloader.autodiscover()


class SimplifiedFeedbackDraftTestBase(testhelper.TestHelper):
    # The SimplifiedFeedbackDraft (from examiner of administrator)
    #SimplifiedFeedbackDraft = ....

    def setUp(self):
        self.create_superuser('superuser')
        self.add(nodes='uni',
                 subjects=['inf101'],
                 periods=['spring01'],
                 assignments=['assignment1:admin(goodadmin,secondgoodadmin)', 'assignment2:admin(badadmin)'])
        self.add_to_path('uni;inf101.spring01.assignment1.group1:candidate(firststudent):examiner(goodexaminer)')
        self.add_to_path('uni;inf101.spring01.assignment1.group2:candidate(secondstudent):examiner(badexaminer)')
        group = self.inf101_spring01_assignment1_group1
        self.delivery = self.add_delivery(group)
        self._setup_users()

        Config.objects.create(assignment=self.inf101_spring01_assignment1,
                              gradeeditorid='asminimalaspossible',
                              config='')

    def _create_draft_without_simplified(self, saved_by):
        return FeedbackDraft.objects.create(delivery=self.delivery,
                                            draft='true',
                                            saved_by=saved_by)

    #def _setup_users(self):
        #
        #Setup:
        #    self.gooduser = #  A user that HAS permissions on FeedbackDraft for self.delivery
        #    self.baduser = # A user that does NOT have permissions on FeedbackDraft for self.delivery




class SimplifiedFeedbackDraftCreateTestBase(SimplifiedFeedbackDraftTestBase):
    def _create_success_test(self, user):
        id = self.SimplifiedFeedbackDraft.create(user,
                                                 delivery=self.delivery,
                                                 draft='true')
        draft = FeedbackDraft.objects.get(id=id) # Will fail if it does not exist
        self.assertFalse(draft.published)
        self.assertEquals(None, draft.staticfeedback)

    def test_create_as_gooduser(self):
        self._create_success_test(self.gooduser)

    def test_create_validation_error(self):
        with self.assertRaises(ValidationError):
            self.SimplifiedFeedbackDraft.create(self.gooduser,
                                                delivery=self.delivery,
                                                draft='really true')

    def test_create_as_baduser(self):
        with self.assertRaises(PermissionDenied):
            self.SimplifiedFeedbackDraft.create(self.baduser,
                                                delivery=self.delivery,
                                                draft='true')

    def test_publish_success(self):
        id = self.SimplifiedFeedbackDraft.create(self.gooduser,
                                                 delivery=self.delivery,
                                                 draft='true',
                                                 published=True)
        draft = FeedbackDraft.objects.get(id=id)
        self.assertTrue(draft.published)
        self.assertTrue(draft.staticfeedback != None)
        self.assertTrue(draft.staticfeedback.is_passing_grade)
        self.assertEquals(draft.staticfeedback.grade, 'approved')
        self.assertEquals(draft.staticfeedback.points, 1)
        self.assertEquals(draft.staticfeedback.rendered_view, 'Your grade is: approved')


class SimplifiedFeedbackDraftReadTestBase(SimplifiedFeedbackDraftTestBase):

    def _read_success_test(self, user):
        draft = self._create_draft_without_simplified(user)
        result = self.SimplifiedFeedbackDraft.read(user, draft.id)
        self.assertEquals(result['draft'], draft.draft)

    def test_read_as_gooduser(self):
        self._read_success_test(self.gooduser)

    def test_read_as_baduser(self):
        draft = self._create_draft_without_simplified(self.goodexaminer)
        with self.assertRaises(PermissionDenied):
            self.SimplifiedFeedbackDraft.read(self.baduser, draft.id)

    def test_read_superuser_access(self):
        # Check that superusers do not have access to drafts from other users
        draft = self._create_draft_without_simplified(self.goodexaminer)
        with self.assertRaises(PermissionDenied):
            self.SimplifiedFeedbackDraft.read(self.superuser, draft.id)


class SimplifiedFeedbackDraftSearchTestBase(SimplifiedFeedbackDraftTestBase):
    def _search_success_test(self, user):
        self.assertEquals(0, len(self.SimplifiedFeedbackDraft.search(user)))
        self._create_draft_without_simplified(user)
        self._create_draft_without_simplified(user)
        self.assertEquals(2, len(self.SimplifiedFeedbackDraft.search(user)))

    def test_search_as_gooduser(self):
        self._search_success_test(self.gooduser)

    def test_search_as_baduser(self):
        draft = self._create_draft_without_simplified(self.gooduser)
        self.assertEquals(0, len(self.SimplifiedFeedbackDraft.search(self.baduser)))

    def test_search_superuser_access(self):
        # Check that superusers do not have access to drafts from other users
        draft = self._create_draft_without_simplified(self.gooduser)
        self.assertEquals(0, len(self.SimplifiedFeedbackDraft.search(self.superuser)))
