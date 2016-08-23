from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from devilry.devilry_markup.views import DevilryFlavouredMarkdownFull

urlpatterns = [
    url(r'^devilry_flavoured_markdown_full$', login_required(DevilryFlavouredMarkdownFull.as_view()))
]
