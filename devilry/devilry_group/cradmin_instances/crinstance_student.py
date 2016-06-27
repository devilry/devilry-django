from __future__ import unicode_literals

from django.db import models
from django.db.models.functions import Lower, Concat
from django_cradmin import crinstance

from devilry.apps.core.models import AssignmentGroup, Candidate, Examiner
from devilry.devilry_group.cradmin_instances import crinstance_base
from devilry.devilry_group.views import feedbackfeed_student
from devilry.devilry_student.cradminextensions import devilry_crmenu_student
from devilry.devilry_student.views.group import projectgroupapp


class Menu(devilry_crmenu_student.Menu):
    def build_menu(self):
        super(Menu, self).build_menu()
        group = self.request.cradmin_role
        self.add_role_menuitem_object()
        self.add_allperiods_breadcrumb_item()
        self.add_singleperiods_breadcrumb_item(period=group.period)
        self.add_group_breadcrumb_item(group=group, active=True)


class StudentCrInstance(crinstance_base.CrInstanceBase):
    menuclass = Menu
    roleclass = AssignmentGroup
    apps = [
        ('projectgroup', projectgroupapp.App),
        ('feedbackfeed', feedbackfeed_student.App)
    ]
    id = 'devilry_group_student'
    rolefrontpage_appname = 'feedbackfeed'

    def get_rolequeryset(self):
        return AssignmentGroup.objects\
            .filter_student_has_access(self.request.user)\
            .select_related('parentnode__parentnode__parentnode')\
            .prefetch_related(
                models.Prefetch('candidates',
                                queryset=self._get_candidatequeryset()))\
            .prefetch_related(
                models.Prefetch('examiners',
                                queryset=self._get_examinerqueryset()))

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/devilry_group/student')

    def get_devilryrole_for_requestuser(self):
        """
        Get the devilryrole for the requesting user on the current
        assignment (request.cradmin_instance).

        The return values is the same as for
        :meth:`devilry.devilry_account.models.PeriodPermissionGroupQuerySet.get_devilryrole_for_user_on_period`,
        except that this method raises ValueError if it does not find a role.
        """
        return 'student'
