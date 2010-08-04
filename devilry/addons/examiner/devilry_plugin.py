from django.utils.translation import ugettext as _

from devilry.addons.dashboard.dashboardplugin_registry import registry, \
        DashboardItem
import dashboardviews


registry.register_important(DashboardItem(
         title = _('Examiner'),
         examiner_access = True,
         view = dashboardviews.simpleview))
