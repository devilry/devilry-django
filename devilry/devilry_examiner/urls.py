from django.conf.urls import patterns, url, include

from devilry.devilry_examiner.views.dashboard import crinstance_dashboard

urlpatterns = patterns(
    '',
    # url(r'^assignment/', include(crinstance_assignment.CrAdminInstance.urls())),
    url(r'^', include(crinstance_dashboard.CrAdminInstance.urls())),
)
