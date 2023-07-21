from django.urls import path
from django.contrib.auth.decorators import login_required

from devilry.devilry_markup.views import DevilryFlavouredMarkdownFull

urlpatterns = [
    path('devilry_flavoured_markdown_full', login_required(DevilryFlavouredMarkdownFull.as_view()))
]
