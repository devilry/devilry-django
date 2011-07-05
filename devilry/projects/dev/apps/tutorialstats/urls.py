from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

import restful
import views

urlpatterns = patterns('devilry.projects.dev.apps.tutorialstats',
    restful.RestStatConfig.create_rest_url(),
    restful.RestPeriodPoints.create_rest_url(),
    url(r'^$',
        login_required(views.main),
        name='tutorialstats-main'),
)
