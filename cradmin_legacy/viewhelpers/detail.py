from django.views.generic.detail import DetailView as DjangoDetailView
from cradmin_legacy.viewhelpers.mixins import QuerysetForRoleMixin


class DetailView(QuerysetForRoleMixin, DjangoDetailView):
    """
    Base detail view for Django cradmin views.
    """


class DetailRoleView(DetailView):
    """
    Extends :class:`.DetailView` to streamline creating a detail view
    for the current role object.

    Just like :class:`.DetailView`, but with the get_object and
    get_queryset_for_role methods implemented to edit the current role
    object.
    """

    def get_object(self, queryset=None):
        return self.get_queryset_for_role(self.request.cradmin_role).get()

    def get_queryset_for_role(self, role):
        return self.model.objects.filter(pk=role.pk)
