from django.conf.urls import url

from devilry.devilry_settings import views

urlpatterns = [
    url(r'^missing_setting/(\w+)$', views.missing_setting, name='devilry_settings_missing_setting'),
]
