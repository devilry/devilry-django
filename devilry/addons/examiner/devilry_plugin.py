from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

from devilry.addons.dashboard.dashboardplugin_registry import registry, \
        DashboardItem


def simpleview(request, *args):
    return mark_safe(u"""Examiner dashboard-view(s) is not finished.
        <a href='/examiner/choose-assignment'>Click here</a> for the
        main examiner view.""")

registry.register_important(DashboardItem(
         title = _('Examiner'),
         examiner_access = True,
         view = simpleview))
