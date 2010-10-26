from django.core.urlresolvers import reverse

from devilry.addons.admin.actionregistry import periodactions


periodactions.add_action(
    label = "stats",
    urlcallback = lambda p:
        reverse('devilry-gradestats-periodstats', args=[str(p.id)])
)
