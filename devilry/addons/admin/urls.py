from django.conf.urls.defaults import *


generic_urls = []
for x in ('node', 'subject', 'period', 'assignment', 'assignmentgroup'):
    generic_urls += [
        url(r'^%ss/edit/(?P<obj_id>\d+)$' % x, 'views.edit_%s' % x,
            name='devilry-admin-edit_%s' % x),
        url(r'^%ss/add/$' % x, 'views.edit_%s' % x,
            name='devilry-admin-add_%s' % x),
        url(r'^%ss/$' % x, 'views.list_%ss' % x,
            name='devilry-admin-list_%ss' % x)]

urlpatterns = patterns('devilry.addons.admin',
    url(r'^$', 'views.main', name='devilry-admin-main'),
    *generic_urls
)
