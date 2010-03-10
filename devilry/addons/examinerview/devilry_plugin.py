from django.utils.translation import ugettext as _
from devilry.addons.dashboard.dashboardplugin_registry import register

register('correctdelivery_key', 
         'Correct Delivery', 
         '/examinerview/', 
         'ikon.png', 
         description = _('Correct delivery.'))
