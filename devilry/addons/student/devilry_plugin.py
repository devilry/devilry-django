from django.utils.translation import ugettext as _

from devilry.addons.quickdash.dashboardplugin_registry import registry, \
        DashboardItem

import dashboardviews


studentgroup = registry.create_group('student', _('Student'))

studentgroup.additems(
        DashboardItem(
            id = 'assignments',
            title = _('Assignments'),
            view = dashboardviews.list_assignments))
