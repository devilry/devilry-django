from django.views.generic import ListView
from django.views.generic import TemplateView
from devilry.apps.core.models import Period

class BrowseView(ListView):
    """

    This view list every course that the student are affiliated with

    """
    template_name = "devilry_student/browseview.django.html"
    model = Period
    paginate_by = 100

    def __init__(self):
        super(BrowseView, self).__init__()

    def get_queryset(self):
        user = self.request.user
        queryset = Period.objects.filter(Period.q_is_relatedstudent(user)).order_by('-start_time', 'long_name')
        return queryset