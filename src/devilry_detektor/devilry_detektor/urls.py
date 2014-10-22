from django.conf.urls.defaults import patterns, url

from .views import admin_assignmentassembly

urlpatterns = patterns(
    'devilry_detektor',
    url(r'^admin/assignmentassembly/(?P<assignmentid>\d+)$',
        admin_assignmentassembly.AssignmentAssemblyView.as_view(),
        name='devilry_detektor_admin_assignmentassembly'),
    )

