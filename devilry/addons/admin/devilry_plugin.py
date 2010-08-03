from django.utils.translation import ugettext as _

from devilry.addons.dashboard.dashboardplugin_registry import registry, \
        DashboardItem
import dashboardviews


registry.register_important(DashboardItem(
         title = _('Nodes'),
         view = dashboardviews.list_nodes,
         admin_access=True,
))

registry.register_important(DashboardItem(
         title = _('Subjects'),
         view = dashboardviews.list_subjects,
         admin_access=True,
))

registry.register_important(DashboardItem(
         title = _('Periods'),
         view = dashboardviews.list_periods,
         admin_access=True,
))

registry.register_important(DashboardItem(
         title = _('Assignments'),
         view = dashboardviews.list_assignments,
         admin_access=True,
))
