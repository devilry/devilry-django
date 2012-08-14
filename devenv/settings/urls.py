from django.conf.urls.defaults import patterns, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import View

from devilry.apps.core import pluginloader
from devilry_settings.default_urls import devilry_urls


class RedirectToFrontpage(View):
    def get(self, request):
        return redirect(reverse('devilry_student'))


urlpatterns = patterns('',
                       # Custom urls for this project
                       (r'^$', RedirectToFrontpage.as_view()),
                       (r'^devilry_subjectadmin/', include('devilry_subjectadmin.urls')),
                       (r'^devilry_student/', include('devilry_student.urls')),

                       # Add the default Devilry urls
                       *devilry_urls
) + staticfiles_urlpatterns()


# Must be after url-loading to allow plugins to use reverse()
pluginloader.autodiscover()
