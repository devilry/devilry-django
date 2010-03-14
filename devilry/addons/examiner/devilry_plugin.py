from django.utils.translation import ugettext as _
from devilry.addons.dashboard.dashboardplugin_registry import register

register('correct_deliveries_key', 
         'Correct Deliveries', 
         '/examiner/choose-assignment', 
         description = _('Correct deliveries.'),
         icon='ikon.png',
         examiner_access=True,
         )
