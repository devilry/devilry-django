from django.views.generic import TemplateView

from cradmin_legacy.viewhelpers import listbuilder


class ItemFrameDjangoApp(listbuilder.itemframe.Link):
    valuealias = "djangoappconfig"

    def get_url(self):
        return self.djangoappconfig.get_indexview_url()


class ItemValueDjangoApp(listbuilder.itemvalue.FocusBox):
    valuealias = "djangoappconfig"
    template_name = "cradmin_legacy/superuserui/listbuilder/itemvalue-djangoapp.django.html"


class View(TemplateView):
    template_name = "cradmin_legacy/superuserui/dashboard.django.html"

    def get_djangoapps_listbuilder_list(self):
        return listbuilder.lists.RowList.from_value_iterable(
            value_iterable=self.request.cradmin_instance.get_superuserui_registry().iter_djangoappconfigs(),
            frame_renderer_class=ItemFrameDjangoApp,
            value_renderer_class=ItemValueDjangoApp,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["djangoapps_list"] = self.get_djangoapps_listbuilder_list()
        context["pagetitle"] = self.request.cradmin_instance.get_superuserui_registry().get_title()
        return context
