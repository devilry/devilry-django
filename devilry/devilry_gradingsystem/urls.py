from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from devilry.django_decoupled_docs.registry import documentationregistry
from devilry.project.common.docproxies import DevilryDocsProxy
from .views.admin.select_points_to_grade_mapper import SelectPointsToGradeMapperView
from .views.admin.selectplugin import SelectPluginView
from .views.admin.setmaxpoints import SetMaxPointsView
from .views.admin.setpassing_grade_min_points import SetPassingGradeMinPointsView
from .views.admin.setup_custom_table import SetupCustomTableView
from .views.admin.summary import SummaryView
from .views.download_feedbackdraftfile import DownloadFeedbackDraftFileView
from .views.feedbackdraft_bulkpreview import FeedbackDraftBulkPreviewView
from .views.feedbackdraft_preview import FeedbackDraftPreviewView

urlpatterns = [
    url('^feedbackdraft_preview/(?P<deliveryid>\d+)/(?P<draftid>\d+)$',
        login_required(FeedbackDraftPreviewView.as_view()),
        name='devilry_gradingsystem_feedbackdraft_preview'),
    url('^feedbackdraft_bulkpreview/(?P<assignmentid>\d+)/(?P<randomkey>[0-9_.-]+)$',
        login_required(FeedbackDraftBulkPreviewView.as_view()),
        name='devilry_gradingsystem_feedbackdraft_bulkpreview'),
    url('^feedbackdraftfile/(?P<pk>\d+)/(?P<asciifilename>.+)?$',
        login_required(DownloadFeedbackDraftFileView.as_view()),
        name='devilry_gradingsystem_feedbackdraftfile'),

    url('^admin/summary/(?P<assignmentid>\d+)$',
        login_required(SummaryView.as_view()),
        name='devilry_gradingsystem_admin_summary'),
    url('^admin/selectplugin/(?P<assignmentid>\d+)$',
        login_required(SelectPluginView.as_view()),
        name='devilry_gradingsystem_admin_selectplugin'),
    url('^admin/setmaxpoints/(?P<assignmentid>\d+)$',
        login_required(SetMaxPointsView.as_view()),
        name='devilry_gradingsystem_admin_setmaxpoints'),
    url('^admin/select_points_to_grade_mapper/(?P<assignmentid>\d+)$',
        login_required(SelectPointsToGradeMapperView.as_view()),
        name='devilry_gradingsystem_admin_select_points_to_grade_mapper'),
    url('^admin/setup_custom_table/(?P<assignmentid>\d+)$',
        login_required(SetupCustomTableView.as_view()),
        name='devilry_gradingsystem_admin_setup_custom_table'),
    url('^admin/setpassing_grade_min_points/(?P<assignmentid>\d+)$',
        login_required(SetPassingGradeMinPointsView.as_view()),
        name='devilry_gradingsystem_admin_setpassing_grade_min_points'),
]


documentationregistry.add('devilry_gradingsystem/markdown', DevilryDocsProxy(
    en='user/markdown.html'))
