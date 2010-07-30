from django.conf.urls.defaults import *

urlpatterns = patterns('devilry.ui',
    url(r'^logout$', 'views.logout_view', name='logout'),
    url(r'^login$', 'views.login_view', name='login'),
    url(r'^download-file/(?P<filemeta_id>\d+)$', 'views.download_file', name='devilry-ui-download_file'),
    url(r'^user_json$', 'views.user_json', name='devilry-ui-user_json'),
    url(r'^preview_rst$', 'views.preview_rst', name='devilry-ui-rst_to_html'),
)

