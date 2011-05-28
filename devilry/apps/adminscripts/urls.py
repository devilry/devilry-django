from django.conf.urls.defaults import *

urlpatterns = patterns('devilry.apps.adminscripts',
    url(r'^dbsanity-check$', 'views.dbsanity_check',
        name='devilry-adminscripts-dbsanity_check'),
    url(r'^dbsanity-fix$', 'views.dbsanity_fix',
        name='devilry-adminscripts-dbsanity_fix'),
)

