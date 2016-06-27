from django.db import models
from django.db.models.functions import Concat, Lower
from django.utils.translation import ugettext_lazy as _
from django_cradmin import crmenu
from django_cradmin import crinstance

from devilry.devilry_account.models import PeriodPermissionGroup
from devilry.apps.core.models import AssignmentGroup, Examiner, Candidate
from devilry.devilry_group.cradmin_instances import crinstance_base
from devilry.devilry_group.views import feedbackfeed_admin


class Menu(crmenu.Menu):
    def build_menu(self):
        group = self.request.cradmin_role
        self.add_headeritem(
            label=group.subject.long_name,
            url=self.appindex_url('feedbackfeed'))


class AdminCrInstance(crinstance_base.CrInstanceBase):
    menuclass = Menu
    roleclass = AssignmentGroup
    apps = [
        ('feedbackfeed', feedbackfeed_admin.App)
    ]
    id = 'devilry_group_admin'
    rolefrontpage_appname = 'feedbackfeed'

    def get_rolequeryset(self):
        return AssignmentGroup.objects.filter_user_is_admin(user=self.request.user)\
            .select_related('parentnode__parentnode__parentnode')\
            .prefetch_related(
                models.Prefetch('candidates',
                                queryset=self._get_candidatequeryset()))\
            .prefetch_related(
                models.Prefetch('examiners',
                                queryset=self._get_examinerqueryset()))

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
