from django.conf.urls import patterns, url, include

from devilry.devilry_admin.views.node import crinstance_node
from devilry.devilry_admin.views.subject import crinstance_subject
from devilry.devilry_admin.views.period import crinstance_period
from devilry.devilry_admin.views.assignment import crinstance_assignment

urlpatterns = patterns(
    '',
    url(r'^node/', include(crinstance_node.CrAdminInstance.urls())),
    url(r'^subject/', include(crinstance_subject.CrAdminInstance.urls())),
    url(r'^period/', include(crinstance_period.CrAdminInstance.urls())),
    url(r'^assignment/', include(crinstance_assignment.CrAdminInstance.urls())),
)
