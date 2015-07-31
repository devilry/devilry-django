from django.conf.urls import patterns, url, include

from devilry.devilry_admin.cradmin_instances import crinstance_period

urlpatterns = patterns(
    '',
    url(r'^period/', include(crinstance_period.CrAdminInstance.urls())),
)
