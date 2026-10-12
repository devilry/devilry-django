from django_cradmin.viewhelpers.listbuilder import base


class RowList(base.List):
    def get_test_css_class_suffixes_list(self):
        css_class_suffixes = super(RowList, self).get_test_css_class_suffixes_list()
        css_class_suffixes.append("cradmin-listbuilder-list")
        return css_class_suffixes

    def get_base_css_classes_list(self):
        css_classes = super(RowList, self).get_base_css_classes_list()
        css_classes.append("blocklist")
        return css_classes
