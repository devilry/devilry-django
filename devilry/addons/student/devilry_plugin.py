from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from devilry.addons.quickdash.dashboardplugin_registry import (registry, 
        DashboardView, DashboardItem, personalgroup)
from devilry.core.models import AssignmentGroup

import dashboardviews

def is_student(request):
    return AssignmentGroup.where_is_candidate(request.user).count() > 0

personalgroup.additems(
    DashboardItem(
        title = _('Assignments'),
        url = reverse('devilry-student-list_assignments'),
        check = is_student),
)

registry.add_view(DashboardView(dashboardviews.student_important))
