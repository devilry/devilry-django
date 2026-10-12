from django.views.generic import TemplateView

from cradmin_legacy.viewhelpers import listbuilder


class ItemFrameModel(listbuilder.itemframe.Link):
    valuealias = "modelconfig"

    def get_url(self):
        return self.modelconfig.get_indexview_url()


class ItemValueModel(listbuilder.itemvalue.FocusBox):
    valuealias = "modelconfig"
    template_name = "cradmin_legacy/superuserui/listbuilder/itemvalue-model.django.html"


class View(TemplateView):
    template_name = "cradmin_legacy/superuserui/appdashboard.django.html"

    def get_models_listbuilder_list(self):
        return listbuilder.lists.RowList.from_value_iterable(
            value_iterable=self.request.cradmin_app.djangoappconfig.iter_modelconfigs(),
            frame_renderer_class=ItemFrameModel,
            value_renderer_class=ItemValueModel,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["models_list"] = self.get_models_listbuilder_list()
        context["djangoappconfig"] = self.request.cradmin_app.djangoappconfig
        return context
