from django.urls import re_path

from cradmin_legacy.apps.cradmin_email.views import email_design

urlpatterns = [
    re_path(r"^emaildesign/(?P<format>html|plaintext)?$", email_design.EmailDesignView.as_view()),
]
