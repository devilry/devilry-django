
from django.conf.urls.defaults import *

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
)
