from django_cradmin import viewhelpers


class UiFormsOverview(viewhelpers.generic.WithinRoleTemplateView):
    template_name = "uicontainerdemo/uicontainer_overview_app/uicontainer_overview.django.html"
