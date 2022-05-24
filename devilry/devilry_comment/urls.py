from django.urls import path

from devilry.devilry_comment.api import preview_markdown


urlpatterns = [
    path('_api/preview-markdown',
        preview_markdown.MarkdownPreviewApi.as_view(),
        name='devilry_comment_api_preview_markdown')
]