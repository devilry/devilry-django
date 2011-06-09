from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

import examiner
import administrator

#def nologin_required(f):
    #return f
#login_required = nologin_required

def nologin_required(f):
    return f
login_required = nologin_required

urlpatterns = patterns('devilry.apps.restful',
    url(r'^examiner/tree/$',
        login_required(examiner.RestSubject.as_view()),
        name='devilry-restful-examiner-tree-subject'),
    url(r'^examiner/tree/(?P<subject_short_name>\w+)/$',
        login_required(examiner.RestPeriod.as_view()),
        name='devilry-restful-examiner-tree-period'),
    url(r'^examiner/tree/(?P<subject_short_name>\w+)/(?P<period_short_name>\w+)/$',
        login_required(examiner.RestAssignment.as_view()),
        name='devilry-restful-examiner-tree-assignment'),

    url(r'^examiner/assignments/$',
        login_required(examiner.RestAssignment.as_view()),
        name='devilry-restful-examiner-assignment'),
    url(r'^examiner/groups/(?P<assignment_id>\d+)/$',
        login_required(examiner.RestAssignmentGroup.as_view()),
        name='devilry-restful-examiner-group'),

    url(r'^administrator/nodes/$',
        login_required(administrator.RestNode.as_view()),
        name='devilry-restful-administrator-nodesearch'),

    url(r'^administrator/nodes/(?P<pk>\d+)$',
        login_required(administrator.RestNode.as_view()),
        name='devilry-restful-administrator-node'),
)
