from django.utils.translation import ugettext as _
from django.conf import settings

from devilry.addons.dashboard.dashboardplugin_registry import registry, \
        DashboardItem
import dashboardviews


#registry.register_important(DashboardItem(
         #title = _('Assignment groups'),
         #examiner_access = True,
         #view = dashboardviews.list_assignmentgroups,
         #js = [settings.DEVILRY_RESOURCES_URL +
             #'/ui/js/jquery.autocompletetable.js']
#))

registry.register_important(DashboardItem(
         title = _('Assignments'),
         examiner_access = True,
         view = dashboardviews.list_assignments,
         js = [settings.DEVILRY_RESOURCES_URL +
             '/ui/js/jquery.autocompletetable.js']
))
