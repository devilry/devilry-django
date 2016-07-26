from django.conf.urls import url, include

from devilry.devilry_admin.views.assignment import crinstance_assignment
from devilry.devilry_admin.views.dashboard import crinstance_dashboard
from devilry.devilry_admin.views.period import crinstance_period
from devilry.devilry_admin.views.subject import crinstance_subject

urlpatterns = [
    url(r'^subject/', include(crinstance_subject.CrAdminInstance.urls())),
    url(r'^period/', include(crinstance_period.CrAdminInstance.urls())),
    url(r'^assignment/', include(crinstance_assignment.CrAdminInstance.urls())),
    url(r'^', include(crinstance_dashboard.CrAdminInstance.urls())),
]
