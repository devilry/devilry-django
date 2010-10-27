from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from devilry.core.models import AssignmentGroup
from devilry.addons.quickdash.dashboardplugin_registry import (registry, 
        DashboardView, DashboardItem, examinergroup)

import dashboardviews


def is_examiner(request):
    return AssignmentGroup.active_where_is_examiner(request.user).count() > 0

examinergroup.additems(
    DashboardItem(
        title = _('Assignments'),
        url = reverse('devilry-examiner-list_assignments'),
        check = is_examiner),
)


registry.add_view(DashboardView(dashboardviews.list_assignments))
