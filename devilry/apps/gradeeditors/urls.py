from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required


from views import LoadGradeEditor


urlpatterns = patterns('devilry.apps.gradeeditors',
                       url(r'^load-grade-editor/(?P<assignmentid>\d+)',
                           login_required(LoadGradeEditor.as_view()))
                      )
