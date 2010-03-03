from django.conf.urls.defaults import *

urlpatterns = patterns('devilry.ui',
    url(r'^logout$', 'views.logout_view', name='logout'),
    url(r'^login$', 'views.login_view', name='login'),
)

