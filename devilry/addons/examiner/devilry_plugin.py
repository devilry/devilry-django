from django.utils.translation import ugettext as _
from django.conf import settings

from devilry.addons.quickdash.dashboardplugin_registry import registry, \
        DashboardItem

import dashboardviews

studentgroup = registry.create_group('examiner', _('Examiner'))


studentgroup.additems(DashboardItem(
    id = 'examine',
    title = _('Assignments'),
    view = dashboardviews.list_assignments,
    js = [settings.DEVILRY_RESOURCES_URL +
        '/ui/js/jquery.autocompletetable.js']
))
