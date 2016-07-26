from django.conf.urls import url

from devilry.devilry_help.views import HelpView

urlpatterns = [
    url('^$', HelpView.as_view(), name='devilry-help'),
]
