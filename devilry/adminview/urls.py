from django.conf.urls.defaults import *


generic_urls = []
for x in ('node', 'subject', 'period', 'assignment'):
    generic_urls += [
        url(r'^%ss/edit/(?P<node_id>\d+)$' % x,
            'views.edit_%s' % x, name='edit-%s' % x),
        url(r'^%ss/add$' % x,
            'views.edit_%s' % x, name='add-%s' % x),
        url(r'^%ss/$' % x,
            'views.list_%ss' % x, name='list-%ss' % x)]

urlpatterns = patterns('devilry.adminview',
    url(r'^$', 'views.main', name='main'),
    *generic_urls
)
