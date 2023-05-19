from django.urls import re_path, path, include

from devilry.devilry_examiner.views.assignment import crinstance_assignment
from devilry.devilry_examiner.views.dashboard import crinstance_dashboard
from devilry.devilry_examiner.views.selfassign import crinstance_selfassign
from devilry.devilry_examiner.views.selfassign import api

urlpatterns = [
    path('assignment/', include(crinstance_assignment.CrAdminInstance.urls())),
    path('self-assign/', include(crinstance_selfassign.CrAdminInstance.urls())),
    path('', include(crinstance_dashboard.CrAdminInstance.urls())),
    re_path('_api/selfassign-to-assignment-group/(?P<period_id>\d+)$',
        api.ExaminerSelfAssignApi.as_view(),
        name='devilry_examiner_selfassign_api')
]
