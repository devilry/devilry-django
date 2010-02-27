from django.conf import settings
from django.contrib.auth.models import User, check_password
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission


#class DevilryPermissions(object):
    #""" """
    #supports_object_permissions = True
    #def has_perm(self, user_obj, perm, obj=None):
        #print perm
        #app_label, codename = perm.split('.', 1)
        ##print perm, app_label, codename
        #perminstance = Permission.objects.get(codename=codename, content_type__app_label=app_label)
        ##print perminstance, dir(perminstance)
        ##print perminstance.name, perminstance.codename
        #model = perminstance.content_type.model_class()
        #if hasattr(model, 'studentobjects'):
            #if model.studentobjects(user_obj).filter().count() > 0:
                #return True
        #if hasattr(model, 'examinerobjects'):
            #if model.examinerobjects(user_obj).filter().count() > 0:
                #return True
        #if hasattr(model, 'adminobjects'):
            #if model.adminobjects(user_obj).filter().count() > 0:
                #return True
        #return False

    #def has_module_perms(self, user_obj, app_label):
        ##print user_obj, app_label
        #return True

    #def get_groups_permissions(self, obj = None):
        #return []





class DjangoModelBackend(ModelBackend):
    supports_object_permissions = True

    def get_group_permissions(self, user_obj, obj=None):
        return []

    def get_all_permissions(self, user_obj, obj=None):
        return []

    def has_perm(self, user_obj, perm, obj=None):
        app_label, codename = perm.split('.', 1)
        perminstance = Permission.objects.get(codename=codename, content_type__app_label=app_label)
        model = perminstance.content_type.model_class()
        if obj and hasattr(obj, 'user_has_obj_perm'):
            return obj.user_has_obj_perm(user_obj, perm)
        if hasattr(model, 'user_has_model_perm'):
            return model.user_has_model_perm(user_obj, perm)
        return False

    def has_module_perms(self, user_obj, app_label, obj=None):
        return True




#class SettingsBackend(DevilryPermissions):
    #"""
    #Authenticate against the settings ADMIN_LOGIN and ADMIN_PASSWORD.

    #Use the login name, and a hash of the password ('test' in the example). For example:

    #ADMIN_LOGIN = 'admin'
    #ADMIN_PASSWORD = 'sha1$7b509$a73b4c9c803a2d5224c98f51f29630e77dce1ef4'
    #"""
    #def authenticate(self, username=None, password=None):
        #login_valid = (settings.ADMIN_LOGIN == username)
        #pwd_valid = check_password(password, settings.ADMIN_PASSWORD)
        #if login_valid and pwd_valid:
            #try:
                #user = User.objects.get(username=username)
            #except User.DoesNotExist:
                ## Create a new user. Note that we can set password
                ## to anything, because it won't be checked; the password
                ## from settings.py will.
                #user = User(username=username, password='get from settings.py')
                #user.is_staff = True
                #user.is_superuser = False
                #user.save()
            #return user
        #return None

    #def get_user(self, user_id):
        #try:
            #return User.objects.get(pk=user_id)
        #except User.DoesNotExist:
            #return None
