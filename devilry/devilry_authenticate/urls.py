from devilry.devilry_authenticate.views import CustomLoginView, DataportenOauthRedirectView
from django.conf.urls import url, include

from django_cradmin.apps.cradmin_authenticate.views import logout

urlpatterns = [
    url(r'^login$', CustomLoginView.as_view(), name='cradmin-authenticate-login'),
    url(r'^logout$', logout.cradmin_logoutview, name='cradmin-authenticate-logout'),
    url(r'^allauth/', include('allauth.urls')),
    url(r'^dataporten/oauth-successful-login-callback$',
        DataportenOauthRedirectView.as_view(),
        name='devilry-authenticate-dataporten-oauth-success'),
]
