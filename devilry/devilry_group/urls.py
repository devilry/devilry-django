# -*- coding: utf-8 -*-

# django imports
from django.urls import path, include

# devilry imports
from devilry.devilry_group.cradmin_instances import crinstance_admin
from devilry.devilry_group.cradmin_instances import crinstance_examiner
from devilry.devilry_group.cradmin_instances import crinstance_student

urlpatterns = [
    path('student/', include(crinstance_student.StudentCrInstance.urls())),
    path('examiner/', include(crinstance_examiner.ExaminerCrInstance.urls())),
    path('admin/', include(crinstance_admin.AdminCrInstance.urls())),
]
