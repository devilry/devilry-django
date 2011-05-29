from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('devilry.apps.restful',
    url(r'^$',
        'views.examples',
        name='devilry-restful-examples'),
)
