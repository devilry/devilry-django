from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.i18n import javascript_catalog

from devilry_settings.i18n import get_javascript_catalog_packages
from .views import QualifiesBasedOnManualSelectView

i18n_packages = get_javascript_catalog_packages('devilry_header', 'devilry.apps.core')



urlpatterns = patterns('devilry_qualifiesforexam_points',
    url('^all/$', login_required(QualifiesBasedOnManualSelectView.as_view()),
        name='devilry_qualifiesforexam_select'),
    url('^i18n.js$', javascript_catalog, kwargs={'packages': i18n_packages},
        name='devilry_qualifiesforexam_select_i18n')
)

