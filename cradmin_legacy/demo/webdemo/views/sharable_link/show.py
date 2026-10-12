from django.urls import reverse
from cradmin_legacy.demo.webdemo.views.sharable_link.mixins import QuerysetForRoleMixin
from cradmin_legacy.viewhelpers.detail import DetailView


class ShowView(QuerysetForRoleMixin, DetailView):
    template_name = "webdemo/sharable_link/show.django.html"
    context_object_name = "generictoken"

    def get_object(self, queryset=None):
        return self.get_queryset().first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        generictoken = context["object"]
        if generictoken:
            url = reverse("webdemo-inviteadmins-public-accept", kwargs={"token": generictoken.token})
            context["url"] = self.request.build_absolute_uri(url)
        return context
