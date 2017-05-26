from django import test
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from model_mommy import mommy

from .importer_testcase_mixin import ImporterTestCaseMixin
from devilry.devilry_import_v2database.models import ImportedModel
from devilry.devilry_import_v2database.modelimporters.user_importer import UserImporter
from devilry.devilry_account.models import UserEmail, UserName


class TestUserImporter(ImporterTestCaseMixin, test.TestCase):

    def _create_model_meta(self):
        return {
            'model_class_name': 'User',
            'max_id': 16,
            'app_label': 'auth'
        }

    def _create_user_dict(self):
        return {
            'pk': 1,
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

    def test_importer(self):
        self.create_v2dump(model_name='auth.user',
                           data=self._create_user_dict())
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        self.assertEquals(get_user_model().objects.count(), 1)

    def test_importer_pk(self):
        self.create_v2dump(model_name='auth.user',
                           data=self._create_user_dict())
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        user = get_user_model().objects.first()
        self.assertEquals(user.pk, 1)
        self.assertEquals(user.id, 1)

    def test_importer_lastname(self):
        self.create_v2dump(model_name='auth.user',
                           data=self._create_user_dict())
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        user = get_user_model().objects.first()
        self.assertEquals(user.lastname, 'Duck')

    def test_importer_short_name(self):
        self.create_v2dump(model_name='auth.user',
                           data=self._create_user_dict())
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        user = get_user_model().objects.first()
        self.assertEquals(user.shortname, 'april')

    def test_importer_is_active(self):
        self.create_v2dump(model_name='auth.user',
                           data=self._create_user_dict())
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        user = get_user_model().objects.first()
        self.assertTrue(user.is_active)

    def test_importer_is_superuser(self):
        self.create_v2dump(model_name='auth.user',
                           data=self._create_user_dict())
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        user = get_user_model().objects.first()
        self.assertFalse(user.is_superuser)

    def test_importer_is_staff(self):
        self.create_v2dump(model_name='auth.user',
                           data=self._create_user_dict())
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        user = get_user_model().objects.first()
        self.assertFalse(user.is_staff)

    def test_importer_password(self):
        self.create_v2dump(model_name='auth.user',
                           data=self._create_user_dict())
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        user = get_user_model().objects.first()
        self.assertEquals(user.password, 'md5$krPxlZzbpjsm$8f4799f31464dfd7f907d4321883afcf')

    def test_importer_useremail(self):
        self.create_v2dump(model_name='auth.user',
                           data=self._create_user_dict())
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        self.assertEquals(UserEmail.objects.count(), 1)
        user_email = UserEmail.objects.first()
        user = get_user_model().objects.first()
        self.assertEquals(user_email.email, 'april@example.com')
        self.assertEquals(user_email.user, user)

    def test_importer_username(self):
        self.create_v2dump(model_name='auth.user',
                           data=self._create_user_dict())
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        self.assertEquals(UserName.objects.count(), 1)
        username = UserName.objects.first()
        user = get_user_model().objects.first()
        self.assertEquals(username.username, 'april')
        self.assertEquals(username.user, user)

    def test_importer_imported_model_created(self):
        user_data_dict = self._create_user_dict()
        self.create_v2dump(model_name='auth.user',
                           data=user_data_dict)
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        user = get_user_model().objects.first()
        self.assertEquals(ImportedModel.objects.count(), 1)
        imported_model = ImportedModel.objects.get(
            content_object_id=user.id,
            content_type=ContentType.objects.get_for_model(model=user)
        )
        self.assertEquals(imported_model.content_object, user)
        self.assertEquals(imported_model.data, user_data_dict)

    def test_auto_sequence_numbered_objects_uses_meta_max_id(self):
        self.create_v2dump(model_name='auth.user',
                           data=self._create_user_dict(),
                           model_meta=self._create_model_meta())
        userimporter = UserImporter(input_root=self.temp_root_dir)
        userimporter.import_models()
        self.assertEquals(get_user_model().objects.count(), 1)
        user = get_user_model().objects.first()
        self.assertEquals(user.pk, 1)
        self.assertEquals(user.id, 1)
        user_with_auto_id = mommy.make(settings.AUTH_USER_MODEL)
        self.assertEquals(user_with_auto_id.id, self._create_model_meta()['max_id']+1)
        self.assertEquals(user_with_auto_id.pk, self._create_model_meta()['max_id']+1)
