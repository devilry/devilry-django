import shutil

from django import test
from django.contrib.auth import get_user_model

from .importer_testcase_mixin import ImporterTestCaseMixin
from devilry.devilry_import_v2database.modelimporters.userimporter import UserImporter
from devilry.devilry_account.models import User


test_user_april = {
    'pk': 3,
    'fields': {
        'username': 'april',
        'first_name': 'April',
        'last_name': 'Duck',
        'is_active': True,
        'is_superuser': False,
        'is_staff': False,
        'last_login': '2017-05-15T11:04:46.531',
        'groups': [],
        'user_permissions': [],
        'password': 'md5$krPxlZzbpjsm$8f4799f31464dfd7f907d4321883afcf',
        'email': 'april@example.com',
        'date_joined': '2017-05-15T11:04:46.531'
    }
}


class TestUserImporter(ImporterTestCaseMixin, test.TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.create_v2dump(model_name='auth.user', data=test_user_april)

    def test_import_user_from_dump(self):
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        self.assertEquals(self.user_model.objects.count(), 1)

    def test_import_user_from_dump_attributes(self):
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        self.assertEquals(self.user_model.objects.count(), 1)
        user = self.user_model.objects.first()
        self.assertEquals(user.pk, test_user_april['pk'])
        self.assertEquals(user.lastname, 'Duck')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertEquals(user.password, test_user_april['fields']['password'])
