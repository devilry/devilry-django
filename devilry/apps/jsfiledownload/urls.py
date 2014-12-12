from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from views import SaveAs, Open

urlpatterns = patterns('devilry.apps.jsfiledownload',
                       url(r'^saveas$', login_required(SaveAs.as_view())),
                       url(r'^open$', login_required(Open.as_view())),
                       )
