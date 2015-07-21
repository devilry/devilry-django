from django.conf.urls import patterns, url, include

from devilry.devilry_group.cradmin_instances import crinstance_student
from devilry.devilry_group.cradmin_instances import crinstance_examiner
from devilry.devilry_group.cradmin_instances import crinstance_subjectadmin
from devilry.devilry_group.cradmin_instances import crinstance_nodeadmin

urlpatterns = patterns(
    'devilry.devilry_group',
    url(r'^student/', include(crinstance_student.StudentCrInstance.urls())),
    url(r'^examiner/', include(crinstance_examiner.ExaminerCrInstance.urls())),
    url(r'^nodeadmin/', include(crinstance_nodeadmin.NodeAdminCrInstance.urls())),
    url(r'^subjectadmin/', include(crinstance_subjectadmin.SubjectAdminCrInstance.urls())),
)