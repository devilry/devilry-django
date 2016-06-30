from django.db import models
from django_cradmin import crmenu

from devilry.devilry_account.models import PeriodPermissionGroup
from devilry.apps.core.models import AssignmentGroup
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
    apps = [
        ('feedbackfeed', feedbackfeed_admin.App)
    ]
    id = 'devilry_group_admin'

    def get_rolequeryset(self):
        """
        Get the base rolequeryset from
        :func:`~devilry.devilry_group.cradmin_instances.CrInstanceBase._get_base_rolequeryset` and filter on user.

        Returns:
            QuerySet: A queryset of :class:`~devilry.apps.core.models.AssignmentGroup`s
                the ``request.user`` is admin on.
        """
        return self._get_base_rolequeryset()\
            .filter_user_is_admin(user=self.request.user)

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
        if not hasattr(self, '_devilryrole_for_requestuser'):
            self._devilryrole_for_requestuser = self.__get_devilryrole_for_requestuser()
        return self._devilryrole_for_requestuser
