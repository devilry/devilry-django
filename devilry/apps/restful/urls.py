from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required

import examiner

#def nologin_required(f):
    #return f
#login_required = nologin_required

urlpatterns = patterns('devilry.apps.restful',
    url(r'^examiner/tree/$',
        login_required(examiner.RestSubject.as_view()),
        name='devilry-restful-examiner-tree-subjects'),
    url(r'^examiner/tree/(?P<subject_short_name>\w+)/$',
        login_required(examiner.RestPeriod.as_view()),
        name='devilry-restful-examiner-tree-periods'),
    url(r'^examiner/tree/(?P<subject_short_name>\w+)/(?P<period_short_name>\w+)/$',
        login_required(examiner.RestAssignment.as_view()),
        name='devilry-restful-examiner-tree-assignments'),

    url(r'^examiner/assignments/$',
        login_required(examiner.RestAssignment.as_view()),
        name='devilry-restful-examiner-assignments'),
    url(r'^examiner/groups/(?P<assignment_id>\d+)/$',
        login_required(examiner.RestGroup.as_view()),
        name='devilry-restful-examiner-groups'),
)
