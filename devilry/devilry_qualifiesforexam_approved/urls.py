from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.i18n import javascript_catalog

from devilry.project.common.i18n import get_javascript_catalog_packages
from .views import AllApprovedView
from .views import SubsetApprovedView


i18n_packages = get_javascript_catalog_packages('devilry_header', 'devilry.apps.core')



urlpatterns = patterns('devilry.devilry_qualifiesforexam_approved',
    url('^all/$', login_required(AllApprovedView.as_view()),
        name='devilry_qualifiesforexam_approved_all'),
    url('^subset/$', login_required(SubsetApprovedView.as_view()),
        name='devilry_qualifiesforexam_approved_subset'),
    url('^i18n.js$', javascript_catalog, kwargs={'packages': i18n_packages},
        name='devilry_qualifiesforexam_approved_i18n')
)

