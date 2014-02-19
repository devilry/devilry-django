from django.conf.urls.defaults import patterns, url
from django.views.i18n import javascript_catalog
from django.contrib.auth.decorators import login_required

from devilry_settings.i18n import get_javascript_catalog_packages
from restful import administrator_restful
from views import (MainView, RestfulSimplifiedView,
                   RestfulSimplifiedViewWithGradeEditors)

i18n_packages = get_javascript_catalog_packages('devilry.apps.administrator', 'devilry.apps.examiner', 'devilry.apps.extjshelpers', 'devilry_header', 'devilry.apps.core')

urlpatterns = patterns('devilry.apps.administrator',
                       url(r'^$',
                           login_required(MainView.as_view()),
                           name='administrator'),
                       RestfulSimplifiedView.as_url('node',
                                                    'administrator/node.django.js'),
                       RestfulSimplifiedView.as_url('subject',
                                                    'administrator/subject.django.js'),
                       RestfulSimplifiedView.as_url('period',
                                                    'administrator/period.django.js'),
                       RestfulSimplifiedViewWithGradeEditors.as_url('assignment',
                                                                    'administrator/assignment.django.js'),
                       RestfulSimplifiedViewWithGradeEditors.as_url('assignmentgroup',
                                                                    'administrator/assignmentgroupview.django.js'),
                       url('^i18n.js$', javascript_catalog, kwargs={'packages': i18n_packages},
                           name='devilry_administrator_i18n')
                      )
urlpatterns += administrator_restful
