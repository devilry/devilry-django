from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required

from views import RestUser

urlpatterns = patterns('devilry.addons.guiexamples',
    url(r'^$',
        'views.main',
        name='devilry-guiexamples-main'),
    url(r'^help$',
        'views.help',
        name='devilry-guiexamples-help'),
    url(r'^assignmentgroups-qry$',
        'views.assignmentgroups_qry',
        name='devilry-guiexamples-assignmentgroups_qry'),
    url(r'^assignment-avg-data$',
        'views.assignment_avg_data',
        name='devilry-guiexamples-assignment_avg_data'),
    url(r'^assignment-avg-labels$',
        'views.assignment_avg_labels',
        name='devilry-guiexamples-assignment_avg_labels'),
    url(r'^all-users/$',
        login_required(RestUser.as_view()),
        name='devilry-guiexamples-restusers-get-all'),
    url(r'^all-users/(?P<username>\w+)$',
        login_required(RestUser.as_view()),
        name='devilry.guiexamples.RestUsers'),
    #url(r'^all-users/$',
        #'views.all_users',
        #name='devilry-guiexamples-all_users'),
    #url(r'^all-users/(?P<username>\w+)$',
        #'views.update_user',
        #name='devilry-guiexamples-update_user'),
)
