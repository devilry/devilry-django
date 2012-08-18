from django.conf.urls.defaults import patterns, url

from .rest import LanguageSelect

urlpatterns = patterns('devilry_i18n',
                       url(r'^rest/languageselect$', LanguageSelect.as_view())
                      )
