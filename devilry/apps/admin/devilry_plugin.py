from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from devilry.addons.quickdash.dashboardplugin_registry import registry, \
        DashboardItem, admingroup, DashboardView
from devilry.core.models import Node, Subject, Period, Assignment

import dashboardviews


def permcheck(nodecls, request):
    if request.user.is_superuser:
        return True
    else:
        return nodecls.where_is_admin_or_superadmin(request.user).count() > 0


admingroup.additems(
    DashboardItem(
        title = _('Nodes'),
        url = reverse('devilry-admin-list_nodes'),
        check = lambda r: permcheck(Node, r)),
    DashboardItem(
        title = _('Subjects'),
        url = reverse('devilry-admin-list_subjects'),
        check = lambda r: permcheck(Subject, r)),
    DashboardItem(
        title = _('Periods'),
        url = reverse('devilry-admin-list_periods'),
        check = lambda r: permcheck(Period, r)),
    DashboardItem(
        title = _('Assignments'),
        url = reverse('devilry-admin-list_assignments'),
        check = lambda r: permcheck(Assignment, r)),
)

registry.add_view(DashboardView(dashboardviews.main))
