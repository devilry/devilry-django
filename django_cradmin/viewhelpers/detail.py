from django.views.generic.detail import DetailView as DjangoDetailView

from django_cradmin import javascriptregistry
from django_cradmin.viewhelpers.mixins import QuerysetForRoleMixin, CommonCradminViewMixin


class DetailView(
    javascriptregistry.viewmixin.WithinRoleViewMixin, CommonCradminViewMixin, QuerysetForRoleMixin, DjangoDetailView
):
    """
    Base detail view for Django cradmin views.

    .. note:: You should import this class with ``from django_cradmin import viewhelpers``,
        and refer to it using ``viewhelpers.detail.DetailView``.
    """

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        self.add_javascriptregistry_component_ids_to_context(context=context)
        self.add_common_view_mixin_data_to_context(context=context)
        return context


class DetailRoleView(DetailView):
    """
    Extends :class:`.DetailView` to streamline creating a detail view
    for the current role object.

    Just like :class:`.DetailView`, but with the get_object and
    get_queryset_for_role methods implemented to edit the current role
    object.

    .. note:: You should import this class with ``from django_cradmin import viewhelpers``,
        and refer to it using ``viewhelpers.detail.DetailRoleView``.
    """

    def get_object(self, queryset=None):
        return self.get_queryset_for_role().get()

    def get_queryset_for_role(self):
        return self.model.objects.filter(pk=self.request.cradmin_role.pk)
