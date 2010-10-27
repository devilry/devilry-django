from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from devilry.addons.admin.actionregistry import periodactions
from devilry.addons.quickdash.dashboardplugin_registry import (
        DashboardItem, personalgroup)
from devilry.core.models import Candidate


periodactions.add_action(
    label = "stats",
    urlcallback = lambda p:
        reverse('devilry-gradestats-periodstats', args=[str(p.id)])
)


#def is_student(user):
    #return Candidate.objects.filter(student=user).count > 0

#personalgroup.additems(
    #DashboardItem(
        #title = _('Grade statistics'),
        #url = "http://example.com",
        #check = lambda r: is_student(r.user)),
#)
