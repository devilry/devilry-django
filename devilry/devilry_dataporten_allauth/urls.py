from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import DevilryDataportenProvider


urlpatterns = default_urlpatterns(DevilryDataportenProvider)