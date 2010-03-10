from django.utils.translation import ugettext as _
from devilry.addons.dashboard.dashboardplugin_registry import register

register('add_delivery_key', 
         'Add Delivery', 
         '/studentview/choose-assignment/', 
         'ikon.png', 
         description = _('Add delivery.'))


register('show_history_key', 
         'Show History', 
         '/studentview/show-history/', 
         'ikon.png', 
         description = _('Show History.'))
