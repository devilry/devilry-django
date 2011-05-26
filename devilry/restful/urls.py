from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required

import examiner

urlpatterns = patterns('devilry.restful',
    url(r'^examples$',
        'views.examples',
        name='devilry-restful-examples'),
    url(r'^examiner/tree/$',
        login_required(examiner.RestSubjects.as_view()),
        name='devilry-restful-examiner-subjects'),
    url(r'^examiner/assignments/$',
        login_required(examiner.RestAssignments.as_view()),
        name='devilry-restful-examiner-assignments'),
    url(r'^examiner/groups/(?P<assignment_id>\d+)/$',
        login_required(examiner.RestGroups.as_view()),
        name='devilry-restful-examiner-groups'),
)
