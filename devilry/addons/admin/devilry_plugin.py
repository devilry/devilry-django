from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.conf import settings

from devilry.addons.dashboard.dashboardplugin_registry import registry, \
        DashboardItem
import dashboardviews


registry.register_normal(DashboardItem(
         title = _('Nodes'),
         view = dashboardviews.list_nodes,
         nodeadmin_access = True,
         js = [settings.DEVILRY_RESOURCES_URL +
             '/ui/js/jquery.autocompletetable.js']
))

registry.register_normal(DashboardItem(
         title = _('Subjects'),
         view = dashboardviews.list_subjects,
         nodeadmin_access = True,
         subjectadmin_access = True,
         js = [settings.DEVILRY_RESOURCES_URL +
             '/ui/js/jquery.autocompletetable.js']
))

registry.register_important(DashboardItem(
         title = _('Periods'),
         view = dashboardviews.list_periods,
         nodeadmin_access = True,
         subjectadmin_access = True,
         periodadmin_access = True,
         js = [settings.DEVILRY_RESOURCES_URL +
             '/ui/js/jquery.autocompletetable.js']
))

registry.register_important(DashboardItem(
         title = _('Assignments'),
         view = dashboardviews.list_assignments,
         nodeadmin_access = True,
         subjectadmin_access = True,
         periodadmin_access = True,
         assignmentadmin_access = True,
         js = [settings.DEVILRY_RESOURCES_URL +
             '/ui/js/jquery.autocompletetable.js']
))
