from django.conf.urls import patterns, url

urlpatterns = patterns(
    'devilry.devilry_settings',
    url(r'^settings.js$', 'views.settings_view', name="devilry-settings"),
    url(r'^missing_setting/(\w+)$', 'views.missing_setting', name='devilry_settings_missing_setting'),
)
