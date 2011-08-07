from django.test import TestCase

from devilry.apps.core import testhelper
from devilry.apps.gradeeditors.simplified import examiner
from devilry.simplified import PermissionDenied
from devilry.apps.gradeeditors.models import Config
from base import (SimplifiedFeedbackDraftCreateTestBase,
                  SimplifiedFeedbackDraftReadTestBase,
                  SimplifiedFeedbackDraftSearchTestBase)

testhelper.TestHelper.set_memory_deliverystore()



class SimplifiedConfigExaminerReadTest(TestCase, testhelper.TestHelper):
    def setUp(self):
        self.add(nodes='uni',
                 subjects=['inf101'],
                 periods=['spring01'],
                 assignments=['assignment1:admin(goodadmin)', 'assignment2:admin(badadmin)'])
        self.add_to_path('uni;inf101.spring01.assignment1.group1:candidate(firststudent):examiner(goodexaminer)')
        self.add_to_path('uni;inf101.spring01.assignment2.group2:candidate(secondstudent):examiner(badexaminer)')

    def test_read_as_goodexaminer(self):
        self.config = self.inf101_spring01_assignment1.gradeeditor_config
        self.config.gradeeditorid = 'fake'
        self.config.config = 'tst'
        self.config.save()
        result = examiner.SimplifiedConfig.read(self.goodexaminer,
                                                self.inf101_spring01_assignment1.id)
        self.assertEquals(result, {'gradeeditorid': u'fake',
                                   'assignment': 1,
                                   'config': u'tst'})

    def test_read_as_badexaminer(self):
        with self.assertRaises(PermissionDenied):
            examiner.SimplifiedConfig.read(self.badexaminer,
                                           self.inf101_spring01_assignment1.id)


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

class SimplifiedFeedbackDraftExaminerCreateTest(SimplifiedFeedbackDraftCreateTestBase, SetupFeedbackDraftTest, TestCase):
    pass

class SimplifiedFeedbackDraftExaminerReadTest(SimplifiedFeedbackDraftReadTestBase, SetupFeedbackDraftTest, TestCase):
    pass

class SimplifiedFeedbackDraftExaminerSearchTest(SimplifiedFeedbackDraftSearchTestBase, SetupFeedbackDraftTest, TestCase):
    pass
