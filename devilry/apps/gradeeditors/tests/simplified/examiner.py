from django.test import TestCase

from devilry.apps.core import testhelper
from devilry.apps.gradeeditors.simplified import examiner
from devilry.simplified import PermissionDenied
from devilry.apps.gradeeditors.models import Config
from base import (SimplifiedFeedbackDraftCreateTestBase,
                  SimplifiedFeedbackDraftReadTestBase,
                  SimplifiedFeedbackDraftSearchTestBase)

testhelper.TestHelper.set_memory_deliverystore()



class SimplifiedConfigAdministratorReadTest(TestCase, testhelper.TestHelper):
    def setUp(self):
        self.add(nodes='uni',
                 subjects=['inf101'],
                 periods=['spring01'],
                 assignments=['assignment1:admin(goodadmin)', 'assignment2:admin(badadmin)'])
        self.add_to_path('uni;inf101.spring01.assignment1.group1:candidate(firststudent):examiner(goodexaminer)')
        self.add_to_path('uni;inf101.spring01.assignment2.group2:candidate(secondstudent):examiner(badexaminer)')

    def test_read_as_goodexaminer(self):
        config = Config.objects.create(gradeeditorid='fake',
                                       assignment=self.inf101_spring01_assignment1,
                                       config='tst')
        result = examiner.SimplifiedConfig.read(self.goodexaminer, config.id)
        self.assertEquals(result, {'gradeeditorid': u'fake',
                                   'assignment': 1,
                                   'config': u'tst', 'id': 1})

    def test_read_as_badexaminer(self):
        config = Config.objects.create(gradeeditorid='fake',
                                       assignment=self.inf101_spring01_assignment1,
                                       config='tst')
        with self.assertRaises(PermissionDenied):
            examiner.SimplifiedConfig.read(self.badexaminer, config.id)


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
