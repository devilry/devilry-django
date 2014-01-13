from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.i18n import javascript_catalog

from devilry_settings.i18n import get_javascript_catalog_packages
from .views.dashboard import DashboardView
from .views.singlegroupoverview import SingleGroupOverview
from .views.allgroupsoverview import AllGroupsOverview
from .views.allgroupsoverview import WaitingForFeedbackOverview
from .views.allgroupsoverview import WaitingForDeliveriesOverview
from .views.allgroupsoverview import CorrectedOverview
from .views.allgroupsoverview import BulkTest
from .views.singledelivery import SingleDeliveryView

i18n_packages = get_javascript_catalog_packages(
    #'devilry_examiner',
    'devilry_extjsextras', 'devilry.apps.core')

urlpatterns = patterns('devilry_examiner',
                       url('^rest/', include('devilry_examiner.rest.urls')),
                       url('^$', login_required(DashboardView.as_view()),
                           name='devilry_examiner_dashboard'),
                       url('^allgroupsoverview/(?P<assignmentid>\d+)$',
                           login_required(AllGroupsOverview.as_view()),
                           name='devilry_examiner_allgroupsoverview'),
                       url('^allgroupsoverview/(?P<assignmentid>\d+)/waiting_for_feedback$',
                           login_required(WaitingForFeedbackOverview.as_view()),
                           name='devilry_examiner_waiting_for_feedback'),
                       url('^allgroupsoverview/(?P<assignmentid>\d+)/waiting_for_deliveries$',
                           login_required(WaitingForDeliveriesOverview.as_view()),
                           name='devilry_examiner_waiting_for_deliveries'),
                       url('^allgroupsoverview/(?P<assignmentid>\d+)/corrected$',
                           login_required(CorrectedOverview.as_view()),
                           name='devilry_examiner_corrected'),
                       url('^bulktest/$',
                           login_required(BulkTest.as_view()),
                           name='devilry_examiner_bulktest'),
                       url('^singlegroupoverview/(?P<groupid>\d+)$',
                           login_required(SingleGroupOverview.as_view()),
                           name='devilry_examiner_singlegroupoverview'),
                       url('^singledelivery/(?P<deliveryid>\d+)$',
                           login_required(SingleDeliveryView.as_view()),
                           name='devilry_examiner_singledeliveryview'),
                       url('^i18n.js$', javascript_catalog,
                           kwargs={'packages': i18n_packages},
                           name='devilry_examiner_i18n')
                       )
