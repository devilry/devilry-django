from django.test import TestCase

from devilry.apps.core import testhelper
from devilry.apps.gradeeditors.simplified import administrator
from devilry.apps.gradeeditors.models import Config
from devilry.simplified import PermissionDenied
from base import (SimplifiedFeedbackDraftCreateTestBase,
                  SimplifiedFeedbackDraftReadTestBase)


testhelper.TestHelper.set_memory_deliverystore()


class SimplifiedConfigAdministratorTestBase(TestCase, testhelper.TestHelper):
    def setUp(self):
        self.create_superuser('superuser')
        self.add(nodes='uni',
                 subjects=['inf101'],
                 periods=['spring01'],
                 assignments=['assignment1:admin(goodadmin)', 'assignment2:admin(badadmin)'])


class SimplifiedConfigAdministratorCreateTest(SimplifiedConfigAdministratorTestBase):
    def _create_success_test(self, user):
        id = administrator.SimplifiedConfig.create(user,
                                                   gradeeditorid='fake',
                                                   assignment=self.inf101_spring01_assignment1,
                                                   config='tst')
        Config.objects.get(id=id) # Will fail if it does not exist

    def test_create_as_goodadmin(self):
        self._create_success_test(self.goodadmin)

    def test_create_as_superuser(self):
        self._create_success_test(self.superuser)

    def test_create_as_badadmin(self):
        with self.assertRaises(PermissionDenied):
            id = administrator.SimplifiedConfig.create(self.badadmin,
                                                       gradeeditorid='fake',
                                                       assignment=self.inf101_spring01_assignment1,
                                                       config='tst')


class SimplifiedConfigAdministratorReadTest(SimplifiedConfigAdministratorTestBase):
    def _read_success_test(self, user):
        config = Config.objects.create(gradeeditorid='fake',
                                       assignment=self.inf101_spring01_assignment1,
                                       config='tst')
        result = administrator.SimplifiedConfig.read(user, config.id)
        self.assertEquals(result, {'gradeeditorid': u'fake',
                                   'assignment': 1,
                                   'config': u'tst', 'id': 1})

    def test_read_as_goodadmin(self):
        self._read_success_test(self.goodadmin)

    def test_read_as_superuser(self):
        self._read_success_test(self.superuser)

    def test_read_as_badadmin(self):
        config = Config.objects.create(gradeeditorid='fake',
                                       assignment=self.inf101_spring01_assignment1,
                                       config='tst')
        with self.assertRaises(PermissionDenied):
            id = administrator.SimplifiedConfig.read(self.badadmin, config.id)


class SimplifiedConfigAdministratorUpdateTest(SimplifiedConfigAdministratorTestBase):
    def setUp(self):
        super(SimplifiedConfigAdministratorUpdateTest, self).setUp()
        self.config = Config.objects.create(gradeeditorid='fake',
                                            assignment=self.inf101_spring01_assignment1,
                                            config='tst')

    def _update_success_test(self, user):
        administrator.SimplifiedConfig.update(user, self.config.id,
                                              gradeeditorid='updated',
                                              assignment=self.inf101_spring01_assignment1,
                                              config='UPDATED')
        updated = Config.objects.get(id=self.config.id)
        self.assertEquals(updated.gradeeditorid, 'updated')
        self.assertEquals(updated.config, 'UPDATED')


    def test_update_as_goodadmin(self):
        self._update_success_test(self.goodadmin)

    def test_update_as_superuser(self):
        self._update_success_test(self.superuser)

    def test_update_as_badadmin(self):
        with self.assertRaises(PermissionDenied):
            administrator.SimplifiedConfig.update(self.badadmin, self.config.id,
                                                  gradeeditorid='updated',
                                                  assignment=self.inf101_spring01_assignment1,
                                                  config='UPDATED')


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
