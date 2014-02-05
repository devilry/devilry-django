from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.i18n import javascript_catalog
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.core.exceptions import ValidationError

from devilry_settings.i18n import get_javascript_catalog_packages
from .views.extjsapp import AppView
from .views.groupinvite_overview import GroupInviteOverviewView
from .views.groupinvite_show import GroupInviteShowView
from .views.groupinvite_delete import GroupInviteDeleteView


i18n_packages = get_javascript_catalog_packages('devilry_student', 'devilry_header', 'devilry_extjsextras', 'devilry.apps.core')


@login_required
def emptyview(request):
    from django.http import HttpResponse
    return HttpResponse('Logged in')


urlpatterns = patterns('devilry_student',
    url('^$', login_required(csrf_protect(ensure_csrf_cookie(AppView.as_view()))),
       name='devilry_student'),
    url('^rest/', include('devilry_student.rest.urls')),
    url('^emptytestview', emptyview), # NOTE: Only used for testing
    url('^i18n.js$', javascript_catalog, kwargs={'packages': i18n_packages},
       name='devilry_student_i18n'),
    url(r'^show_delivery/(?P<delivery_id>\d+)$', 'views.show_delivery.show_delivery',
       name='devilry_student_show_delivery'),
    url(r'^groupinvite/overview/(?P<group_id>\d+)$',
        login_required(GroupInviteOverviewView.as_view()),
        name='devilry_student_groupinvite_overview'),
    url(r'^groupinvite/show/(?P<invite_id>\d+)$',
        login_required(GroupInviteShowView.as_view()),
        name='devilry_student_groupinvite_show'),
    url(r'^groupinvite/remove/(?P<invite_id>\d+)$',
        login_required(GroupInviteDeleteView.as_view()),
        name='devilry_student_groupinvite_delete'),
    #url(r'^groupinvite/leave/(?P<group_id>\d+)$')
)