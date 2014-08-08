import json
from django.test import TestCase

from devilry.apps.core import testhelper
from devilry.apps.gradeeditors.simplified import administrator
from devilry.apps.gradeeditors.models import Config
from devilry.simplified import PermissionDenied
from base import (SimplifiedFeedbackDraftCreateTestBase,
                  SimplifiedFeedbackDraftReadTestBase,
                  SimplifiedFeedbackDraftSearchTestBase)


testhelper.TestHelper.set_memory_deliverystore()


CONFIG = json.dumps({'defaultvalue': False, 'fieldlabel': 'approved?'})


class SimplifiedConfigAdministratorTestBase(TestCase, testhelper.TestHelper):
    def setUp(self):
        self.create_superuser('superuser')
        self.add(nodes='uni',
                 subjects=['inf101'],
                 periods=['spring01'],
                 assignments=['assignment1:admin(goodadmin)', 'assignment2:admin(badadmin)'])



class SimplifiedConfigAdministratorReadTest(SimplifiedConfigAdministratorTestBase):
    def _read_success_test(self, user):
        config = self.inf101_spring01_assignment1.gradeeditor_config
        config.gradeeditorid = 'asminimalaspossible'
        config.config = CONFIG
        config.save()
        result = administrator.SimplifiedConfig.read(user, config.assignment_id)
        self.assertEquals(result, {'gradeeditorid': u'asminimalaspossible',
                                   'assignment': 1,
                                   'config': CONFIG})

    def test_read_as_goodadmin(self):
        self._read_success_test(self.goodadmin)

    def test_read_as_superuser(self):
        self._read_success_test(self.superuser)

    def test_read_as_badadmin(self):
        with self.assertRaises(PermissionDenied):
            id = administrator.SimplifiedConfig.read(self.badadmin, self.inf101_spring01_assignment1.id)


class SimplifiedConfigAdministratorUpdateTest(SimplifiedConfigAdministratorTestBase):
    def setUp(self):
        super(SimplifiedConfigAdministratorUpdateTest, self).setUp()
        self.config = self.inf101_spring01_assignment1.gradeeditor_config
        self.config.gradeeditorid = 'asminimalaspossible'
        self.config.config = CONFIG
        self.config.save()

    def _update_success_test(self, user):
        newconfig = json.dumps({'defaultvalue': True, 'fieldlabel': 'ok?'})
        administrator.SimplifiedConfig.update(user, self.config.assignment_id,
                                              gradeeditorid='asminimalaspossible',
                                              assignment=self.inf101_spring01_assignment1,
                                              config=newconfig)
        updated = Config.objects.get(assignment=self.config.assignment_id)
        self.assertEquals(updated.config, newconfig)


    def test_update_as_goodadmin(self):
        self._update_success_test(self.goodadmin)

    def test_update_as_superuser(self):
        self._update_success_test(self.superuser)

    def test_update_as_badadmin(self):
        newconfig = json.dumps({'defaultvalue': True, 'fieldlabel': 'ok?'})
        with self.assertRaises(PermissionDenied):
            administrator.SimplifiedConfig.update(self.badadmin, self.config.assignment_id,
                                                  gradeeditorid='asminimalaspossible',
                                                  assignment=self.inf101_spring01_assignment1,
                                                  config=newconfig)


#
#
# FeedbackDraft
#
#


class SetupFeedbackDraftTest(object):
    SimplifiedFeedbackDraft = administrator.SimplifiedFeedbackDraft
    def _setup_users(self):
        self.gooduser = self.goodadmin
        self.baduser = self.badadmin

class SimplifiedFeedbackDraftAdministratorCreateTest(SimplifiedFeedbackDraftCreateTestBase, SetupFeedbackDraftTest, TestCase):
    def test_create_as_superuser(self):
        self._create_success_test(self.superuser)

class SimplifiedFeedbackDraftAdministratorReadTest(SimplifiedFeedbackDraftReadTestBase, SetupFeedbackDraftTest, TestCase):
    def test_read_as_superuser(self):
        self._read_success_test(self.superuser)

class SimplifiedFeedbackDraftAdministratorSearchTest(SimplifiedFeedbackDraftSearchTestBase, SetupFeedbackDraftTest, TestCase):
    def test_search_as_superuser(self):
        self._search_success_test(self.superuser)
