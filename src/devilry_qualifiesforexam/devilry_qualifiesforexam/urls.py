from django.conf.urls.defaults import patterns, url, include


urlpatterns = patterns('devilry_qualifiesforexam',
                       url('^rest/', include('devilry_qualifiesforexam.rest.urls'))
                      )

