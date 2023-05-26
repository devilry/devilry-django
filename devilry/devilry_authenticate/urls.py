from django.urls import path, include
from cradmin_legacy.apps.cradmin_authenticate.views import logout

from devilry.devilry_authenticate.views import CustomLoginView, allauth_views

urlpatterns = [
    path('login', CustomLoginView.as_view(), name='cradmin-authenticate-login'),
    path('logout', logout.cradmin_logoutview, name='cradmin-authenticate-logout'),

    path('allauth/login/',
        allauth_views.AllauthLoginView.as_view(),
        # name='account_login'
        name='dataporten_login'
    ),
    path('allauth/logout/',
        allauth_views.AllauthLogoutView.as_view(),
        # name='account_logout'
        name='dataporten_logout'
    ),
    path('allauth/', include('allauth.urls')),
]