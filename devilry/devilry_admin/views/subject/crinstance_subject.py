from devilry.apps.core.models import Subject
from devilry.devilry_account.models import SubjectPermissionGroup
from devilry.devilry_cradmin import devilry_crinstance
from devilry.devilry_admin.cradminextensions import devilry_crmenu_admin
from devilry.devilry_admin.views.subject import admins
from devilry.devilry_admin.views.subject import createperiod
from devilry.devilry_admin.views.subject import overview
from devilry.devilry_admin.views.subject import edit


class Menu(devilry_crmenu_admin.Menu):
    def build_menu(self):
        super(Menu, self).build_menu()
        subject = self.request.cradmin_role
        self.add_role_menuitem_object()
        self.add_subject_breadcrumb_item(subject=subject, active=True)


class CrAdminInstance(devilry_crinstance.BaseCrInstanceAdmin):
    menuclass = Menu
    roleclass = Subject
    apps = [
        ('overview', overview.App),
        ('admins', admins.App),
        ('createperiod', createperiod.App),
        ('edit', edit.App),
    ]
    id = 'devilry_admin_subjectadmin'
    rolefrontpage_appname = 'overview'

    def get_rolequeryset(self):
        return Subject.objects.filter_user_is_admin(user=self.request.user)

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is a Subject.
        """
        subject = role
        return subject

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/devilry_admin/subject')

    def __get_devilryrole_for_requestuser(self):
        subject = self.request.cradmin_role
        devilryrole = SubjectPermissionGroup.objects.get_devilryrole_for_user_on_subject(
            user=self.request.user,
            subject=subject
        )
        if devilryrole is None:
            raise ValueError('Could not find a devilryrole for request.user. This must be a bug in '
                             'get_rolequeryset().')

        return devilryrole

    def get_devilryrole_for_requestuser(self):
        """
        Get the devilryrole for the requesting user on the current
        subject (request.cradmin_instance).

        The return values is the same as for
        :meth:`devilry.devilry_account.models.SubjectPermissionGroupQuerySet.get_devilryrole_for_user_on_subject`,
        exept that this method raises ValueError if it does not find a role.
        """
        if not hasattr(self, '_devilryrole_for_requestuser'):
            self._devilryrole_for_requestuser = self.__get_devilryrole_for_requestuser()
        return self._devilryrole_for_requestuser
