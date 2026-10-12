class QuerySetForRoleMixin:
    def get_model_class(self):
        return self.request.cradmin_app.modelconfig.get_model_class()
        # return self.modelconfig.get_modelclass()

    def get_queryset_for_role(self, role=None):
        return self.get_model_class().objects.all()


class ListFilterQuerySetForRoleMixin:
    def get_model_class(self):
        return self.request.cradmin_app.modelconfig.get_model_class()
        # return self.modelconfig.get_modelclass()

    def get_unfiltered_queryset_for_role(self, role=None):
        return self.get_model_class().objects.all()
