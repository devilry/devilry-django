from django.utils.translation import ugettext as _
from devilry.addons.dashboard.dashboardplugin_registry import register
from django.core.urlresolvers import reverse

register('add_delivery_key', 
         'Add Delivery', 
         reverse('devilry-student-add_delivery_choose_assignment'),
         description = _('Add delivery.'),
         icon='ikon.png',
         student_access=True,
         )


register('show_history_key', 
         'Show History', 
         reverse('devilry-student-show_history'),
         description = _('Show History.'),
         icon='ikon.png', 
         student_access=True,
         )

register('show_assignments_key', 
         'Show Assignments', 
         reverse('devilry-student-show_assignments'),
         description = _('Show Assignments.'),
         icon='ikon.png', 
         student_access=True,
         )
