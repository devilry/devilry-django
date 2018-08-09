import pprint

from django.conf import settings
from django.contrib.auth import get_user_model

from devilry.devilry_account.models import UserName, UserEmail
from devilry.devilry_import_v2database import modelimporter


class UserImporter(modelimporter.ModelImporter):
    def get_model_class(self):
        return get_user_model()

    def _create_username(self, user, username):
        if username == '' or len(username) == 0:
            return
        username_object = UserName(
            user=user,
            username=username,
            is_primary=True)
        if self.should_clean():
            username_object.full_clean()
        else:
            username_object.clean()
        username_object.save()

    def _create_useremail(self, user, email):
        if email == '' or len(email) == 0:
            return
        username_object = UserEmail(
            user=user,
            email=email,
            use_for_notifications=True,
            is_primary=True)
        if self.should_clean():
            username_object.full_clean()
        else:
            username_object.clean()
        username_object.save()

    def _create_user_from_object_dict(self, object_dict):
        user = self.get_model_class()()
        self.patch_model_from_object_dict(
            model_object=user,
            object_dict=object_dict,
            attributes=[
                'pk',
                'is_superuser',
                'password',
                ('last_name', 'lastname')
            ]
        )
        # The shortname is overridden by _create_username() or _create_useremail()
        # depending on the DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND setting
        # (See devilry.devilry_account.models.UserName.clean and
        # devilry.devilry_account.models.UserEmail.clean).
        username = object_dict['fields']['username']
        user.shortname = username
        user.set_unusable_password()
        if self.should_clean():
            user.full_clean()
        user.save()
        email = object_dict['fields']['email']
        if not settings.DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND:
            self._create_username(user=user, username=username)
        self._create_useremail(user=user, email=email)
        self.log_create(model_object=user, data=object_dict)

    def import_models(self, fake=False):
        directory_parser = self.v2user_directoryparser
        directory_parser.set_max_id_for_models_with_auto_generated_sequence_numbers(model_class=self.get_model_class())
        for object_dict in directory_parser.iterate_object_dicts():
            if fake:
                print('Would import: {}'.format(pprint.pformat(object_dict)))
            else:
                self._create_user_from_object_dict(object_dict=object_dict)
