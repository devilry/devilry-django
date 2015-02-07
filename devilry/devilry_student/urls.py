from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django_cradmin import crinstance

from devilry.devilry_student.cradmin_group.projectgroupapp import GroupInviteRespondView
from devilry.devilry_student.cradmin_student import cradmin_student
from devilry.devilry_student.cradmin_period import cradmin_period
from devilry.devilry_student.cradmin_group import cradmin_group
from .views.download_deliveryfiles import CompressedFileDownloadView
from .views.download_deliveryfiles import FileDownloadView


@login_required
def redirect_to_student_frontpage_view(request):
    return redirect(crinstance.reverse_cradmin_url(
        instanceid='devilry_student',
        appname='waitingfordeliveries',
        roleid=request.user.id))


urlpatterns = patterns(
    'devilry.devilry_student',
    url('^$', redirect_to_student_frontpage_view, name='devilry_student'),

    url(r'^groupinvite/respond/(?P<invite_id>\d+)$',
        login_required(GroupInviteRespondView.as_view()),
        name='devilry_student_groupinvite_respond'),

    url(r'^show-delivery/filedownload/(?P<filemetaid>\d+)$',
        login_required(FileDownloadView.as_view()),
        name='devilry-delivery-file-download'),
    url(r'^show-delivery/compressedfiledownload/(?P<deliveryid>\d+)$',
        login_required(CompressedFileDownloadView.as_view()),
        name='devilry-delivery-download-all-zip'),

    url(r'^show_delivery/(?P<delivery_id>\d+)$', 'views.show_delivery.show_delivery',
        name='devilry_student_show_delivery'),

    url(r'^period/', include(cradmin_period.CrAdminInstance.urls())),
    url(r'^group/', include(cradmin_group.CrAdminInstance.urls())),
    url(r'^', include(cradmin_student.CrAdminInstance.urls()))
)
