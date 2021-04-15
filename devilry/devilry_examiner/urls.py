from django.urls import path, include

from devilry.devilry_examiner.views.assignment import crinstance_assignment
from devilry.devilry_examiner.views.dashboard import crinstance_dashboard

urlpatterns = [
    path('assignment/', include(crinstance_assignment.CrAdminInstance.urls())),
    path('', include(crinstance_dashboard.CrAdminInstance.urls())),
]


# from django.conf.urls import url, include

# from devilry.devilry_examiner.views.assignment import crinstance_assignment
# from devilry.devilry_examiner.views.dashboard import crinstance_dashboard

# urlpatterns = [
#     url(r'^assignment/', include(crinstance_assignment.CrAdminInstance.urls())),
#     url(r'^', include(crinstance_dashboard.CrAdminInstance.urls())),
# ]
