from django.conf.urls import include, url

from devilry.devilry_student.views import show_delivery
from devilry.devilry_student.views.dashboard import crinstance_dashboard
from devilry.devilry_student.views.period import crinstance_period

urlpatterns = [
    url(r'^show_delivery/(?P<delivery_id>\d+)$', show_delivery.show_delivery,
        name='devilry_student_show_delivery'),

    url(r'^period/', include(crinstance_period.CrAdminInstance.urls())),
    url(r'^', include(crinstance_dashboard.CrAdminInstance.urls()))
]
