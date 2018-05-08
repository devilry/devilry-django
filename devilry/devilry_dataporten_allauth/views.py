from allauth.socialaccount.providers.dataporten.views import DataportenAdapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2LoginView,
)

from . callback import DevilryOAuth2CallbackView
from .provider import DevilryDataportenProvider


class DevilryDataportenAdapter(DataportenAdapter):
    provider_id = DevilryDataportenProvider.id


oauth2_login = OAuth2LoginView.adapter_view(DevilryDataportenAdapter)
oauth2_callback = DevilryOAuth2CallbackView.adapter_view(DevilryDataportenAdapter)