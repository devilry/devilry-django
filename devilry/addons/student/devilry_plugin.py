from django.utils.translation import ugettext as _
from devilry.addons.dashboard.dashboardplugin_registry import register
from django.core.urlresolvers import reverse

register('show_assignments_key', 
         'Show Assignments', 
         reverse('devilry-student-show-assignments'),
         description = _('Show Assignments.'),
         icon='ikon.png', 
         student_access=True,
         )
