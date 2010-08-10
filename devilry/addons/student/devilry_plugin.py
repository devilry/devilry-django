from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from devilry.addons.dashboard.dashboardplugin_registry import registry, \
        DashboardItem
import dashboardviews

#def simpleview(request, *args):
    #return mark_safe(u"""Student dashboard-view(s) is not finished.
        #<a href='%s'>Click here</a> for the
        #main student view.""" % reverse('devilry-student-show-assignments'))

registry.register_important(DashboardItem(
         title = _('Assignments'),
         candidate_access = True,
         view = dashboardviews.list_assignments))
