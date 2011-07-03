from django.conf.urls.defaults import patterns
from django.contrib.auth.decorators import login_required

from restful import administrator_restful
from views import MainView

urlpatterns = patterns('devilry.apps.administrator',
                      (r'^$', login_required(MainView.as_view())))
urlpatterns += administrator_restful
