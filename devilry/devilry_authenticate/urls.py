from django.conf.urls import url, include
from django_cradmin.apps.cradmin_authenticate.views import logout

from devilry.devilry_authenticate.views import CustomLoginView, allauth_views

urlpatterns = [
    url(r'^login$', CustomLoginView.as_view(), name='cradmin-authenticate-login'),
    url(r'^logout$', logout.cradmin_logoutview, name='cradmin-authenticate-logout'),

    url(r"^allauth/login/$",
        allauth_views.AllauthLoginView.as_view(),
        name="account_login"),
    url(r"^allauth/logout/$",
        allauth_views.AllauthLogoutView.as_view(),
        name="account_logout"),
    url(r'^allauth/', include('allauth.urls')),
]
