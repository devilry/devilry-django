from django.utils.translation import ugettext as _
from devilry.addons.dashboard.dashboardplugin_registry import register

register('correctdelivery_key', 
         'Correct Delivery', 
         '/examiner/choose-assignment', 
         description = _('Correct delivery.'),
         icon='ikon.png',
         examiner_access=True,
         )
