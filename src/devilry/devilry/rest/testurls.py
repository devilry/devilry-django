"""
Urls for the :mod:`.testviews`.
"""
from django.conf.urls.defaults import patterns

from testviews import RestPolls


urlpatterns = patterns('devilry.rest',
                       RestPolls.create_noauth_url("polls",
                                                   "restpolls-api",
                                                   "1.0"))
