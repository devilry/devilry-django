from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required

import examiner

urlpatterns = patterns('devilry.simplified',
    url(r'^examiner/assignments/$',
        login_required(examiner.Assignments.as_view()),
        name='devilry-simplified-examiner-assignments'),
)

