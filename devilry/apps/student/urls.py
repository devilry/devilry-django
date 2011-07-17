from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

from restful import student_restful
from views import MainView

urlpatterns = patterns('devilry.apps.student',
                       url(r'^$', login_required(MainView.as_view()), name='student'),
                           )

urlpatterns += student_restful
