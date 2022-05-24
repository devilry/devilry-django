from django.urls import path

from devilry.devilry_help.views import HelpView

urlpatterns = [
    path('', HelpView.as_view(), name='devilry-help'),
]
