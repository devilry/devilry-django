from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

from views import TranslateGui

urlpatterns = patterns('devilry.apps.i18n',
                       url(r'^translategui$', login_required(TranslateGui.as_view())),
                       )
