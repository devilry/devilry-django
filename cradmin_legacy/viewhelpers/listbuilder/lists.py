from cradmin_legacy.viewhelpers.listbuilder import base


class RowList(base.List):
    def get_base_css_classes_list(self):
        css_classes = super().get_base_css_classes_list()
        css_classes.append("cradmin-legacy-listbuilder-rowlist")
        return css_classes


class FloatGridList(base.List):
    def get_css_size_class(self):
        return "cradmin-legacy-listbuilder-floatgridlist-lg"

    def get_base_css_classes_list(self):
        css_classes = super().get_base_css_classes_list()
        css_classes.append("cradmin-legacy-listbuilder-floatgridlist")
        css_classes.append(self.get_css_size_class())
        return css_classes
