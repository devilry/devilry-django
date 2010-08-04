from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from devilry.addons.dashboard.dashboardplugin_registry import registry, \
        DashboardItem


def simpleview(request, *args):
    return mark_safe(u"""Student dashboard-view(s) is not finished.
        <a href='%s'>Click here</a> for the
        main student view.""" % reverse('devilry-student-show-assignments'))

registry.register_important(DashboardItem(
         title = _('Student'),
         candidate_access = True,
         view = simpleview))


#registry.register('add_delivery_key', 
         #'Add Delivery', 
         #reverse('devilry-student-add_delivery_choose_assignment'),
         #description = _('Add delivery.'),
         #icon='ikon.png',
         #student_access=True,
         #)
#registry.register('show_history_key', 
         #'Show History', 
         #reverse('devilry-student-show_history'),
         #description = _('Show History.'),
         #icon='ikon.png', 
         #student_access=True,
         #)
#registry.register('show_assignments_key', 
         #'Show Assignments', 
         #reverse('devilry-student-show_assignments'),
         #description = _('Show Assignments.'),
         #icon='ikon.png', 
         #student_access=True,
         #)
#register('show_assignments_key', 
         #'Show Assignments', 
         #reverse('devilry-student-show-assignments'),
         #description = _('Show Assignments.'),
         #icon='ikon.png', 
         #student_access=True,
         #)

