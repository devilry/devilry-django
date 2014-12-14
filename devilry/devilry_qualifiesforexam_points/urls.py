from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.i18n import javascript_catalog

from devilry.project.common.i18n import get_javascript_catalog_packages
from .views import QualifiesBasedOnPointsView


i18n_packages = get_javascript_catalog_packages('devilry_header', 'devilry.apps.core')



urlpatterns = patterns('devilry.devilry_qualifiesforexam_points',
    url('^all/$', login_required(QualifiesBasedOnPointsView.as_view()),
        name='devilry_qualifiesforexam_points'),
    url('^i18n.js$', javascript_catalog, kwargs={'packages': i18n_packages},
        name='devilry_qualifiesforexam_points_i18n')
)

