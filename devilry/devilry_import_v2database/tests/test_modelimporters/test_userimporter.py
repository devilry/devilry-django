from django import test
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from .importer_testcase_mixin import ImporterTestCaseMixin
from devilry.devilry_import_v2database.models import ImportedModel
from devilry.devilry_import_v2database.modelimporters.userimporter import UserImporter
from devilry.devilry_account.models import UserEmail, UserName

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

    def test_importer(self):
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        self.assertEquals(self.user_model.objects.count(), 1)

    def test_importer_pk(self):
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        user = self.user_model.objects.first()
        self.assertEquals(user.pk, 3)

    def test_importer_lastname(self):
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        user = self.user_model.objects.first()
        self.assertEquals(user.lastname, 'Duck')

    def test_importer_short_name(self):
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        user = self.user_model.objects.first()
        self.assertEquals(user.shortname, 'april')

    def test_importer_is_active(self):
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        user = self.user_model.objects.first()
        self.assertTrue(user.is_active)

    def test_importer_is_superuser(self):
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        user = self.user_model.objects.first()
        self.assertFalse(user.is_superuser)

    def test_importer_is_staff(self):
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        user = self.user_model.objects.first()
        self.assertFalse(user.is_staff)

    def test_importer_password(self):
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        user = self.user_model.objects.first()
        self.assertEquals(user.password, 'md5$krPxlZzbpjsm$8f4799f31464dfd7f907d4321883afcf')

    def test_importer_useremail(self):
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        self.assertEquals(UserEmail.objects.count(), 1)
        user_email = UserEmail.objects.first()
        user = self.user_model.objects.first()
        self.assertEquals(user_email.email, 'april@example.com')
        self.assertEquals(user_email.user, user)

    def test_importer_username(self):
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        self.assertEquals(UserName.objects.count(), 1)
        username = UserName.objects.first()
        user = self.user_model.objects.first()
        self.assertEquals(username.username, 'april')
        self.assertEquals(username.user, user)

    def test_importer_imported_model_created(self):
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        self.assertEquals(ImportedModel.objects.count(), 1)
        imported_model = ImportedModel.objects.first()
        self.assertEquals(imported_model.data, test_user_april)
