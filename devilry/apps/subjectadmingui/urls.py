from django.conf.urls.defaults import patterns, url
from devilry.apps.guibase.views import GuiBaseView

urlpatterns = patterns('devilry.apps.subjectadmingui',
                       url(r'^$', GuiBaseView.as_appview('subjectadmingui')))
