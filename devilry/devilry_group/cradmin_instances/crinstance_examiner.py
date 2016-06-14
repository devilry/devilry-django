from django.db import models
from django.db.models.functions import Lower, Concat
from django_cradmin import crinstance
from django_cradmin import crmenu

from devilry.apps.core.models import AssignmentGroup, Candidate, Examiner
from devilry.devilry_examiner.cradminextensions import devilry_crmenu_examiner
from devilry.devilry_group.views import feedbackfeed_examiner


class Menu(devilry_crmenu_examiner.Menu):
    def build_menu(self):
        super(Menu, self).build_menu()
        group = self.request.cradmin_role
        self.add_role_menuitem_object()
        self.add_assignment_breadcrumb_item(assignment=group.assignment)
        self.add_group_breadcrumb_item(group=group, active=True)


class ExaminerCrInstance(crinstance.BaseCrAdminInstance):
    menuclass = Menu
    roleclass = AssignmentGroup
    apps = [
        ('feedbackfeed', feedbackfeed_examiner.App)
    ]
    id = 'devilry_group_examiner'
    rolefrontpage_appname = 'feedbackfeed'

    def get_rolequeryset(self):
        candidatequeryset = Candidate.objects\
            .select_related('relatedstudent')\
            .order_by(
                Lower(Concat('relatedstudent__user__fullname',
                             'relatedstudent__user__shortname')))
        examinerqueryset = Examiner.objects\
            .select_related('relatedexaminer')\
            .order_by(
                Lower(Concat('relatedexaminer__user__fullname',
                             'relatedexaminer__user__shortname')))
        return AssignmentGroup.objects\
            .filter_examiner_has_access(self.request.user)\
            .select_related('parentnode__parentnode__parentnode')\
            .prefetch_related(
                models.Prefetch('candidates',
                                queryset=candidatequeryset))\
            .prefetch_related(
                models.Prefetch('examiners',
                                queryset=examinerqueryset))

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is an AssignmentGroup.
        """
        return "{} - {}".format(role.period, role.assignment.short_name)

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/devilry_group/examiner')

    def get_devilryrole_for_requestuser(self):
        """
        Get the devilryrole for the requesting user on the current
        assignment (request.cradmin_instance).

        The return values is the same as for
        :meth:`devilry.devilry_account.models.PeriodPermissionGroupQuerySet.get_devilryrole_for_user_on_period`,
        exept that this method raises ValueError if it does not find a role.
        """
        return 'examiner'
