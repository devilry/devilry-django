from django.conf.urls.defaults import patterns
from django.contrib.auth.decorators import login_required

import restful
from views import MainView

urlpatterns = patterns('devilry.apps.administrator',
                      restful.RestfulSimplifiedNode.create_rest_url(),
                      restful.RestfulSimplifiedSubject.create_rest_url(),
                      restful.RestfulSimplifiedPeriod.create_rest_url(),
                      (r'^$', login_required(MainView.as_view())))
