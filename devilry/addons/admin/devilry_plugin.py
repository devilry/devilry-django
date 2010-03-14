from django.utils.translation import ugettext as _
from devilry.addons.dashboard.dashboardplugin_registry import register

register('admin_dashboard', 
         'Admin Dashboard', 
         '/admin/', 
         description = _('Admin Dashboard.'),
         icon='ikon.png',
         admin_access=True,
         )
