from django.urls import path, re_path, include
from django.contrib.auth.decorators import login_required

from devilry.devilry_student.views import show_delivery
from devilry.devilry_student.views.dashboard import crinstance_dashboard
from devilry.devilry_student.views.group.projectgroupapp import GroupInviteRespondViewStandalone
from devilry.devilry_student.views.period import crinstance_period

urlpatterns = [
    re_path(r'^groupinvite/respond/(?P<invite_id>\d+)$',
        login_required(GroupInviteRespondViewStandalone.as_view()),
        name='devilry_student_groupinvite_respond'),

    re_path(r'^show_delivery/(?P<delivery_id>\d+)$', show_delivery.show_delivery,
        name='devilry_student_show_delivery'),

    path('period/', include(crinstance_period.CrAdminInstance.urls())),
    path('', include(crinstance_dashboard.CrAdminInstance.urls()))
]

# from django.conf.urls import include, url
# from django.contrib.auth.decorators import login_required

# from devilry.devilry_student.views import show_delivery
# from devilry.devilry_student.views.dashboard import crinstance_dashboard
# from devilry.devilry_student.views.group.projectgroupapp import GroupInviteRespondViewStandalone
# from devilry.devilry_student.views.period import crinstance_period

# urlpatterns = [
#     url(r'^groupinvite/respond/(?P<invite_id>\d+)$',
#         login_required(GroupInviteRespondViewStandalone.as_view()),
#         name='devilry_student_groupinvite_respond'),

#     url(r'^show_delivery/(?P<delivery_id>\d+)$', show_delivery.show_delivery,
#         name='devilry_student_show_delivery'),

#     url(r'^period/', include(crinstance_period.CrAdminInstance.urls())),
#     url(r'^', include(crinstance_dashboard.CrAdminInstance.urls()))
# ]
