from django.utils.translation import ugettext as _
from django.conf import settings

from devilry.addons.quickdash.dashboardplugin_registry import registry, \
        DashboardItem, admingroup

import dashboardviews


admingroup.additems(
    #DashboardItem(
        #id = 'assignments',
        #title = _('Assignments'),
        #view = dashboardviews.list_assignments,
        #js = [settings.DEVILRY_RESOURCES_URL +
            #'/ui/js/jquery.autocompletetable.js']),
    #DashboardItem(
        #id = 'periods',
        #title = _('Periods'),
        #view = dashboardviews.list_periods,
        #js = [settings.DEVILRY_RESOURCES_URL +
            #'/ui/js/jquery.autocompletetable.js']),
    #DashboardItem(
        #id = 'subjects',
        #title = _('Subjects'),
        #view = dashboardviews.list_subjects,
        #js = [settings.DEVILRY_RESOURCES_URL +
            #'/ui/js/jquery.autocompletetable.js']),
    DashboardItem(
        id = 'nodes',
        title = _('Nodes'),
        view = dashboardviews.list_nodes,
        js = [settings.DEVILRY_RESOURCES_URL +
            '/ui/js/jquery.autocompletetable.js'])
)
