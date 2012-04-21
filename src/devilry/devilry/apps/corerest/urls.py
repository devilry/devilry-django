from django.conf.urls.defaults import patterns, include


urlpatterns = patterns('devilry.apps.corerest',
    (r'^administrator/', include('devilry.apps.corerest.administrator.urls'))
)