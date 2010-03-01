from django.conf import settings
from django.contrib.auth.models import User, check_password
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission



class DjangoModelBackend(ModelBackend):
    supports_object_permissions = True

    def get_group_permissions(self, user_obj, obj=None):
        return []

    def get_all_permissions(self, user_obj, obj=None):
        return []

    def has_perm(self, user_obj, perm, obj=None):
        print perm
        app_label, codename = perm.split('.', 1)
        perminstance = Permission.objects.get(codename=codename, content_type__app_label=app_label)
        model = perminstance.content_type.model_class()
        if obj and hasattr(model, 'has_obj_permission'):
            return model.has_obj_permission(user_obj, perm, obj)
        elif hasattr(model, 'has_model_permission'):
            return model.has_model_permission(user_obj, perm)
        return False

    def has_module_perms(self, user_obj, app_label, obj=None):
        return True
