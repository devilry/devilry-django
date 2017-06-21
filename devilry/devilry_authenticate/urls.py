from devilry.devilry_authenticate.views import CustomLoginView
from django.conf.urls import url

from django_cradmin.apps.cradmin_authenticate.views import logout

urlpatterns = [
    url(r'^login$', CustomLoginView.as_view(), name='cradmin-authenticate-login'),
    url(r'^logout$', logout.cradmin_logoutview, name='cradmin-authenticate-logout'),
]
