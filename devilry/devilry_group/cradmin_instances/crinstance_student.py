from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models.functions import Lower, Concat
from django_cradmin import crmenu
from django_cradmin import crinstance

from devilry.apps.core.models import AssignmentGroup, Candidate
from devilry.devilry_group.views import feedbackfeed_student
from devilry.devilry_student.views.group import projectgroupapp


class Menu(crmenu.Menu):
    def build_menu(self):
        group = self.request.cradmin_role
        self.add_headeritem(
            label=group.subject.long_name,
            url=self.appindex_url('feedbackfeed'))

        if group.assignment.students_can_create_groups:
            self.add(
                label=_('Project group'),
                url=self.appindex_url('projectgroup'),
                active=self.request.cradmin_app.appname == 'projectgroup')


class StudentCrInstance(crinstance.BaseCrAdminInstance):
    menuclass = Menu
    roleclass = AssignmentGroup
    apps = [
        ('projectgroup', projectgroupapp.App),
        ('feedbackfeed', feedbackfeed_student.App)
    ]
    id = 'devilry_group_student'
    rolefrontpage_appname = 'feedbackfeed'

    def get_rolequeryset(self):
        candidatequeryset = Candidate.objects\
            .select_related('relatedstudent')\
            .order_by(
                Lower(Concat('relatedstudent__user__fullname',
                             'relatedstudent__user__shortname')))
        return AssignmentGroup.objects\
            .filter_student_has_access(self.request.user)\
            .select_related('parentnode',
                            'parentnode__parentnode',
                            'parentnode__parentnode__parentnode')\
            .prefetch_related(
                models.Prefetch('candidates',
                                queryset=candidatequeryset)
        )

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is an AssignmentGroup.
        """
        return "{} - {}".format(role.period, role.assignment.short_name)

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/devilry_group/student')

    def get_devilryrole_for_requestuser(self):
        """
        Get the devilryrole for the requesting user on the current
        assignment (request.cradmin_instance).

        The return values is the same as for
        :meth:`devilry.devilry_account.models.PeriodPermissionGroupQuerySet.get_devilryrole_for_user_on_period`,
        exept that this method raises ValueError if it does not find a role.
        """
        return 'student'
