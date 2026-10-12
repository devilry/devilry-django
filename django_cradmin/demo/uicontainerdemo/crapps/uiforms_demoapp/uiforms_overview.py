from django_cradmin import viewhelpers


class UiFormsOverview(viewhelpers.generic.WithinRoleTemplateView):
    template_name = "uicontainerdemo/uiforms_demoapp/uiforms_overview.django.html"
