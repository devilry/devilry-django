from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from devilry.addons.dashboard.dashboardplugin_registry import registry, \
        DashboardItem
import dashboardviews

registry.register_important(DashboardItem(
         title = _('Assignments'),
         candidate_access = True,
         view = dashboardviews.list_assignments))
