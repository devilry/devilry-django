from django.conf.urls import patterns, url, include

from devilry.devilry_group.cradmin_instances import crinstance_student
from devilry.devilry_group.cradmin_instances import crinstance_examiner
from devilry.devilry_group.cradmin_instances import crinstance_admin

urlpatterns = patterns(
    'devilry.devilry_group',
    url(r'^student/', include(crinstance_student.StudentCrInstance.urls())),
    url(r'^examiner/', include(crinstance_examiner.ExaminerCrInstance.urls())),
    url(r'^admin/', include(crinstance_admin.AdminCrInstance.urls())),
)