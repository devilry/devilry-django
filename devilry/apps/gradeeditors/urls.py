from django.conf.urls.defaults import patterns, include

from restful.administrator import administrator_restful
from restful.examiner import examiner_restful


administratorurlpatterns = patterns('')
administratorurlpatterns += administrator_restful
examinerurlpatterns = patterns('')
examinerurlpatterns += examiner_restful
urlpatterns = patterns('devilry.apps.gradeeditors',
                       (r'^administrator/', include(administratorurlpatterns)),
                       (r'^examiner/', include(examinerurlpatterns))
                      )
