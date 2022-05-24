from django.utils.safestring import mark_safe
from django.core.exceptions import PermissionDenied
from django.http import Http404

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from devilry.devilry_markup import parse_markdown


class MarkdownPreviewApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        raise Http404()

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied()
        markdown_text = request.data.get('markdown_text', None)
        markdown_result = parse_markdown.markdown_full(markdown_text)
        return Response({'markdown_result': mark_safe(markdown_result)}, status=status.HTTP_200_OK)
