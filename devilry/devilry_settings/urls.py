from django.urls import re_path

from devilry.devilry_settings import views

urlpatterns = [
    re_path('missing_setting/(\w+)$', views.missing_setting, name='devilry_settings_missing_setting'),
]
