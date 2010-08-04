from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.conf import settings

from devilry.addons.dashboard.dashboardplugin_registry import registry, \
        DashboardItem
import dashboardviews


registry.register_normal(DashboardItem(
         title = _('Nodes'),
         view = dashboardviews.list_nodes,
         admin_access=True,
         js = [
             settings.DEVILRY_RESOURCES_URL + '/ui/js/jquery.autocompletetable.js',
             reverse('admin-autocomplete-nodename.js')]
))

registry.register_normal(DashboardItem(
         title = _('Subjects'),
         view = dashboardviews.list_subjects,
         admin_access=True,
         js = [
             settings.DEVILRY_RESOURCES_URL + '/ui/js/jquery.autocompletetable.js',
             reverse('admin-autocomplete-subjectname.js')]
))

registry.register_normal(DashboardItem(
         title = _('Periods'),
         view = dashboardviews.list_periods,
         admin_access=True,
         js = [
             settings.DEVILRY_RESOURCES_URL + '/ui/js/jquery.autocompletetable.js',
             reverse('admin-autocomplete-periodname.js')]
))

registry.register_important(DashboardItem(
         title = _('Assignments'),
         view = dashboardviews.list_assignments,
         admin_access=True,
         js = [
             settings.DEVILRY_RESOURCES_URL + '/ui/js/jquery.autocompletetable.js',
             reverse('admin-autocomplete-assignmentname.js')]
))
