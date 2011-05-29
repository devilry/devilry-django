from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('devilry.apps.restful_examples',
    url(r'^$',
        'views.examples',
        name='devilry-restful-examples'),
)
