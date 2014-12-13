from django.conf.urls import patterns, url

from .rest import LanguageSelect

urlpatterns = patterns('devilry.devilry_i18n',
                       url(r'^rest/languageselect$', LanguageSelect.as_view())
                      )
