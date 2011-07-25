from django.test import TestCase

from devilry.apps.gradeeditors.simplified import examiner
from base import (SimplifiedFeedbackDraftCreateTestBase,
                  SimplifiedFeedbackDraftReadTestBase,
                  SimplifiedFeedbackDraftSearchTestBase)

#
#
# FeedbackDraft
#
#


class SetupFeedbackDraftTest(object):
    SimplifiedFeedbackDraft = examiner.SimplifiedFeedbackDraft
    def _setup_users(self):
        self.gooduser = self.goodexaminer
        self.baduser = self.badexaminer

class SimplifiedFeedbackDraftAdministratorCreateTest(SimplifiedFeedbackDraftCreateTestBase, SetupFeedbackDraftTest, TestCase):
    pass

class SimplifiedFeedbackDraftAdministratorReadTest(SimplifiedFeedbackDraftReadTestBase, SetupFeedbackDraftTest, TestCase):
    pass

class SimplifiedFeedbackDraftAdministratorSearchTest(SimplifiedFeedbackDraftSearchTestBase, SetupFeedbackDraftTest, TestCase):
    pass
