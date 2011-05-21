from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required

import examiner

urlpatterns = patterns('devilry.simplified',
    url(r'^examiner/assignments/$',
        login_required(examiner.Assignments.as_view()),
        name='devilry-simplified-examiner-assignments'),
    url(r'^examiner/groups/(?P<assignment_id>\d+)/$',
        login_required(examiner.Groups.as_view()),
        name='devilry-simplified-examiner-groups'),
)

