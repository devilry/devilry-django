from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.i18n import javascript_catalog
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django_cradmin import crinstance
from devilry.devilry_student.cradmin_student import cradmin_student

from devilry.project.common.i18n import get_javascript_catalog_packages
from devilry.devilry_student.cradmin_period import cradmin_period
from devilry.devilry_student.cradmin_group import cradmin_group
from devilry.devilry_student.views.extjsapp import AppView
from .views.frontpage import FrontpageView
from .views.projectgroup_overview import ProjectGroupOverviewView
from .views.groupinvite_respond import GroupInviteRespondView
from .views.groupinvite_delete import GroupInviteDeleteView
from .views.browseview import BrowseView
from .views.groupdetails import GroupDetailsView
from .views.semesteroverview import SemesterOverview
from .views.download_deliveryfiles import CompressedFileDownloadView
from .views.download_deliveryfiles import FileDownloadView


i18n_packages = get_javascript_catalog_packages('devilry_student', 'devilry_header', 'devilry_extjsextras', 'devilry.apps.core')


@login_required
def emptyview(request):
    from django.http import HttpResponse
    return HttpResponse('Logged in')


@login_required
def redirect_to_student_frontpage_view(request):
    return redirect(crinstance.reverse_cradmin_url(
        instanceid='devilry_student',
        appname='waitingfordeliveries',
        roleid=request.user.id))


urlpatterns = patterns(
    'devilry.devilry_student',
    url('^$', redirect_to_student_frontpage_view, name='devilry_student'),

    url('^old2$', login_required(FrontpageView.as_view())),
    url('^old$', login_required(csrf_protect(ensure_csrf_cookie(AppView.as_view())))),
    url('^rest/', include('devilry.devilry_student.rest.urls')),
    url('^emptytestview', emptyview), # NOTE: Only used for testing
    url('^i18n.js$', javascript_catalog, kwargs={'packages': i18n_packages},
       name='devilry_student_i18n'),
    url(r'^show_delivery/(?P<delivery_id>\d+)$', 'views.show_delivery.show_delivery',
       name='devilry_student_show_delivery'),
    url(r'^groupinvite/overview/(?P<group_id>\d+)$',
        login_required(ProjectGroupOverviewView.as_view()),
        name='devilry_student_projectgroup_overview'),
    url(r'^groupinvite/respond/(?P<invite_id>\d+)$',
        login_required(GroupInviteRespondView.as_view()),
        name='devilry_student_groupinvite_respond'),
    url(r'^groupinvite/remove/(?P<invite_id>\d+)$',
        login_required(GroupInviteDeleteView.as_view()),
        name='devilry_student_groupinvite_delete'),
    url(r'^browse/$',
        login_required(BrowseView.as_view()),
        name='devilry_student_browse'),
    url(r'^browse/period/(?P<pk>\d+)$',
        login_required(SemesterOverview.as_view()),
        name='devilry_student_browseperiod'),
    url(r'^groupdetails/(?P<id>\d+)$',
        login_required(GroupDetailsView.as_view()),
        name='devilry_student_groupdetails'),

    # TODO: Rename the views
    url(r'^show-delivery/filedownload/(?P<filemetaid>\d+)$',
        login_required(FileDownloadView.as_view()),
        name='devilry-delivery-file-download'),
    url(r'^show-delivery/compressedfiledownload/(?P<deliveryid>\d+)$',
        login_required(CompressedFileDownloadView.as_view()),
        name='devilry-delivery-download-all-zip'),

    #url(r'^groupinvite/leave/(?P<group_id>\d+)$')

    url(r'^period/', include(cradmin_period.CrAdminInstance.urls())),
    url(r'^group/', include(cradmin_group.CrAdminInstance.urls())),
    url(r'^', include(cradmin_student.CrAdminInstance.urls()))
)
