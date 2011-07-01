from django.conf.urls.defaults import patterns

import restful
from views import MainView

urlpatterns = patterns('devilry.apps.administrator',
                      restful.RestNode.create_rest_url(),
                      restful.RestSubject.create_rest_url(),
                      restful.RestPeriod.create_rest_url(),
                      (r'^$', MainView.as_view()))
