from django.views.generic import ListView
from django.views.generic import TemplateView


class BrowseView(TemplateView):
    template_name = "devilry_student/browseview.django.html"
    """

    This view list every course that the student are affiliated with

    """
    def __init__(self):
        super(BrowseView, self).__init__()
