from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from devilry.addons.admin.actionregistry import \
        periodactions as admin_periodactions
from devilry.addons.student.actionregistry import \
        periodactions as student_periodactions, \
        groupactions as student_groupactions


admin_periodactions.add_action(
    label = _("Statistics"),
    urlcallback = lambda p:
        reverse('devilry-gradestats-periodstats', args=[str(p.id)])
)

student_periodactions.add_action(
    labelcallback = lambda p:
        _("Statistics for %(period)s")  % dict(
            period=p.get_path()),
    tooltipcallback = lambda p:
        _("Statistics for %(subject)s - %(period)s" % dict(
            subject=p.parentnode.long_name,
            period=p.long_name)),
    urlcallback = lambda p:
        reverse('devilry-gradestats-userstats', args=[str(p.id)])
)
student_groupactions.add_action(
    labelcallback = lambda g:
        _("Statistics for %(period)s")  % dict(
            period=g.parentnode.parentnode.get_path()),
    tooltipcallback = lambda g:
        _("Statistics for %(subject)s - %(period)s" % dict(
            subject=g.parentnode.parentnode.parentnode.long_name,
            period=g.parentnode.parentnode.long_name)),
    urlcallback = lambda g:
        reverse('devilry-gradestats-userstats',
            args=[str(g.parentnode.parentnode.id)])
)
