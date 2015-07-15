from django.contrib.auth import get_user_model
from django_cradmin import crmenu
from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_group.cradmin_feedback_thread import feedbackthreadapp
from devilry.devilry_group.cradminextensions import devilrygroupcrinstance
from devilry.devilry_student.cradmin_group import projectgroupapp


class Menu(crmenu.Menu):
    def build_menu(self):
        self.add(
            # add stuff
        )


class CrAdminInstance(devilrygroupcrinstance.BaseDevilryGroupCrAdminInstance):
    id = 'devilry_group'
    menuclass = Menu
    roleclass = AssignmentGroup
    rolefrontpage_appname = 'feedbackthread'

    apps = [
        ('feedbackthread', feedbackthreadapp.App),
        ('projectgroup', projectgroupapp.App),
    ]

    def get_rolequeryset(self):
        return get_user_model().objects.filter(id=self.request.user.id)

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is a User.
        """
        return str(role.id)

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/some_url/')