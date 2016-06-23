from django.db import models
from django.db.models.functions import Concat
from django.db.models.functions import Lower
from django.utils.translation import ugettext_lazy as _
from django_cradmin import crmenu
from django_cradmin import crinstance

from devilry.devilry_account.models import PeriodPermissionGroup
from devilry.apps.core.models import AssignmentGroup, Examiner, Candidate
from devilry.devilry_group.views import feedbackfeed_admin


class Menu(crmenu.Menu):
    def build_menu(self):
        group = self.request.cradmin_role
        self.add_headeritem(
            label=group.subject.long_name,
            url=self.appindex_url('feedbackfeed'))


class AdminCrInstance(crinstance.BaseCrAdminInstance):
    menuclass = Menu
    roleclass = AssignmentGroup
    apps = [
        ('feedbackfeed', feedbackfeed_admin.App)
    ]
    id = 'devilry_group_admin'
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
        return AssignmentGroup.objects.filter_user_is_admin(user=self.request.user)\
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
        return urlpath.startswith('/devilry_group/admin')

    def __get_devilryrole_for_requestuser(self):
        assignment = self.request.cradmin_role.assignment
        devilryrole = PeriodPermissionGroup.objects.get_devilryrole_for_user_on_period(
            user=self.request.user,
            period=assignment.period
        )
        if devilryrole is None:
            raise ValueError('Could not find a devilryrole for request.user. This must be a bug in '
                             'get_rolequeryset().')
        return devilryrole

    def get_devilryrole_for_requestuser(self):
        """
        Get the devilryrole for the requesting user on the current
        assignment (request.cradmin_instance).

        The return values is the same as for
        :meth:`devilry.devilry_account.models.PeriodPermissionGroupQuerySet.get_devilryrole_for_user_on_period`,
        except that this method raises ValueError if it does not find a role.
        """
        if not hasattr(self, '_devilryrole_for_requestuser'):
            self._devilryrole_for_requestuser = self.__get_devilryrole_for_requestuser()
        return self._devilryrole_for_requestuser
