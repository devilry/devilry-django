from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.i18n import javascript_catalog

from devilry_settings.i18n import get_javascript_catalog_packages
from restful import examiner_restful
from views import (MainView, AssignmentGroupView,
                    AssignmentView, CompressedFileDownloadView)

i18n_packages = get_javascript_catalog_packages('devilry.apps.examiner',
    'devilry.apps.extjshelpers', 'devilry_header',
    'devilry_extjsextras', 'devilry.apps.core')

urlpatterns = patterns('devilry.apps.examiner',
                       url(r'^$', login_required(MainView.as_view()), name='examiner'),
                       url(r'^assignmentgroup/(?P<assignmentgroupid>\d+)$',
                           login_required(AssignmentGroupView.as_view()), name='examiner-agroup-view'),
                       url(r'^assignment/(?P<assignmentid>\d+)$',
                           login_required(AssignmentView.as_view()), name='examiner-assignment-view'),
                       url(r'^assignment/compressedfiledownload/(?P<assignmentid>\d+)$',
                           login_required(CompressedFileDownloadView.as_view())),
                       url('^i18n.js$', javascript_catalog,
                           kwargs={'packages': i18n_packages},
                           name='devilry_examiner_i18n')
                      )

urlpatterns += examiner_restful
