from django.conf.urls import patterns

urlpatterns = patterns('devilry.thirdpartylibs.djangorestframework.utils.staticviews',
    (r'^accounts/login/$', 'api_login'),
    (r'^accounts/logout/$', 'api_logout'),
)
