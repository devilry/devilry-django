from django.conf.urls.defaults import *


generic_urls = []
for x in ('node', 'subject', 'period', 'assignment'):
    generic_urls += [
        (r'^%ss/edit/(?P<node_id>\d+)$' % x, 'views.edit_%s' % x),
        (r'^%ss/add/$' % x, 'views.edit_%s' % x),
        (r'^%ss/$' % x, 'views.list_%ss' % x)]

urlpatterns = patterns('devilry.addons.adminview',
    (r'^$', 'views.main'),
    *generic_urls
)
