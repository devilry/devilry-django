from django.conf.urls.defaults import patterns, include

from restful.administrator import administrator_restful
from restful.examiner import examiner_restful
from views import RestfulGradeEditorConfig


administratorurlpatterns = patterns('')
administratorurlpatterns += administrator_restful
examinerurlpatterns = patterns('')
examinerurlpatterns += examiner_restful
urlpatterns = patterns('devilry.apps.gradeeditors',
                       RestfulGradeEditorConfig.create_rest_url(),
                       (r'^administrator/', include(administratorurlpatterns)),
                       (r'^examiner/', include(examinerurlpatterns))
                      )
