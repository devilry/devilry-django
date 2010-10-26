from django.core.urlresolvers import reverse

from devilry.addons.admin.actionregistry import period_rowactions


period_rowactions.add_action(
    label = "stats",
    urlcallback = lambda p:
        reverse('devilry-gradestats-periodstats', args=[str(p.id)])
)
