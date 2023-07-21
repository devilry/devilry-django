from django.urls import path, include

from devilry.devilry_admin.views.assignment import crinstance_assignment
from devilry.devilry_admin.views.dashboard import crinstance_dashboard
from devilry.devilry_admin.views.period import crinstance_period
from devilry.devilry_admin.views.subject import crinstance_subject
from devilry.devilry_admin.views.subject_for_period_admin import crinstance_subject_for_periodadmin as crinstance_subject_period

urlpatterns = [
    path('subject_for_periodadmin/', include(crinstance_subject_period.CrAdminInstance.urls())),
    path('subject/', include(crinstance_subject.CrAdminInstance.urls())),
    path('period/', include(crinstance_period.CrAdminInstance.urls())),
    path('assignment/', include(crinstance_assignment.CrAdminInstance.urls())),
    path('', include(crinstance_dashboard.CrAdminInstance.urls())),
]