from django.conf.urls.defaults import patterns, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import View
from django.contrib.admin import AdminSite

from devilry.apps.core import pluginloader
from devilry.defaults.urls import devilry_urls


class RedirectToFrontpage(View):
    def get(self, request):
        return redirect(reverse('student'))


# Create the adminsite (for superadmins)
adminsite = AdminSite()
from devilry_useradmin.admin import register_useradmin
register_useradmin(adminsite)



# Setup urls
urlpatterns = patterns('',
                       # Custom urls for this project
                       (r'^$', RedirectToFrontpage.as_view()),
                       (r'^devilry_subjectadmin/', include('devilry_subjectadmin.urls')),
                       (r'^devilry_usersearch/', include('devilry_usersearch.urls')),

                       # Django admin interface
                       (r'^superadmin/', include(adminsite.urls)),

                       # Add the default Devilry urls
                       *devilry_urls
) + staticfiles_urlpatterns()


# Must be after url-loading to allow plugins to use reverse()
pluginloader.autodiscover()
