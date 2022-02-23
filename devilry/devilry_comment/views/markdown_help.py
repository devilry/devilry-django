from django.views.generic import TemplateView


class MarkdownHelpView(TemplateView):
    template_name = 'devilry_comment/markdown_help.django.html'
