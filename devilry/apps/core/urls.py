from django.urls import re_path

from .api.applicationstate import ReadyCheck, LiveCheck

urlpatterns = [
    re_path('_api/application-state/ready', ReadyCheck.as_view(), name='devilry_core_application_state_ready'),
    re_path('_api/application-state/alive', LiveCheck.as_view(), name='devilry_core_application_state_alive'),
]
