from django.contrib.auth import get_user_model
from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _
from django_cradmin import crmenu
from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_group.cradmin_feedback_feed import feedbackfeedapp
from devilry.devilry_group.cradminextensions import devilrygroupcrinstance
from devilry.devilry_student.cradmin_group import projectgroupapp


class Menu(crmenu.Menu):
    def build_menu(self):
        group = self.request.cradmin_role
        self.add_headeritem(
            label=group.subject.long_name,
            url=urlresolvers.reverse('devilry_group-feedbackfeed-INDEX', kwargs={
                'roleid': group.id
            }),
            icon="angle-up")

        if group.assignment.students_can_create_groups:
            self.add(
                label=_('Project group'), url=self.appindex_url('projectgroup'),
                icon="users",
                active=self.request.cradmin_app.appname == 'projectgroup')


class CrAdminInstance(devilrygroupcrinstance.BaseDevilryGroupCrAdminInstance):
    id = 'devilry_group'
    menuclass = Menu
    roleclass = AssignmentGroup
    rolefrontpage_appname = 'feedbackfeed'

    apps = [
        ('feedbackfeed', feedbackfeedapp.App),
        ('projectgroup', projectgroupapp.App),
    ]

    def get_rolequeryset(self):
        return AssignmentGroup.objects\
            .filter_student_has_access(user=self.request.user)

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is a User.
        """
        return str(role.id)

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/devilry_group')