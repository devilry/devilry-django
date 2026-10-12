from django.db import models
from django.utils.translation import gettext_lazy

from cradmin_legacy.superuserui.views import mixins
from cradmin_legacy.viewhelpers import listbuilder
from cradmin_legacy.viewhelpers import listbuilderview
from cradmin_legacy.viewhelpers import listfilter
from cradmin_legacy.viewhelpers import multiselect2


class BaseView(mixins.ListFilterQuerySetForRoleMixin, listbuilderview.FilterListMixin, listbuilderview.View):
    paginate_by = 50

    def get_search_fields(self):
        """
        Get a list with the names of the fields to use while searching.

        Defaults to the ``id`` field and all CharField and TextField on the model.
        """
        fields = ["id"]
        for field in self.get_model_class()._meta.get_fields():
            if isinstance(field, (models.CharField, models.TextField)):
                fields.append(field.name)
        return fields

    def add_filterlist_items(self, filterlist):
        super().add_filterlist_items(filterlist=filterlist)
        search_fields = self.get_search_fields()
        if search_fields:
            filterlist.append(
                listfilter.django.single.textinput.Search(
                    slug="search",
                    label=gettext_lazy("Search"),
                    label_is_screenreader_only=True,
                    modelfields=search_fields,
                )
            )


class View(listbuilderview.ViewCreateButtonMixin, BaseView):
    value_renderer_class = listbuilder.itemvalue.EditDelete

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl("filter", kwargs={"filters_string": filters_string})

    def get_datetime_filter_fields(self):
        return [field for field in self.get_model_class()._meta.get_fields() if isinstance(field, models.DateTimeField)]

    def add_datetime_filters(self, filterlist):
        datetime_filter_fields = self.get_datetime_filter_fields()
        for field in datetime_filter_fields:
            filterlist.append(listfilter.django.single.select.DateTime(slug=field.name, label=field.verbose_name))

    def add_filterlist_items(self, filterlist):
        super().add_filterlist_items(filterlist=filterlist)
        self.add_datetime_filters(filterlist=filterlist)


class ForeignKeySelectView(BaseView):
    value_renderer_class = listbuilder.itemvalue.UseThis
    hide_menu = True

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            "foreignkeyselect-filter", kwargs={"filters_string": filters_string}
        )


class ManyToManySelectView(multiselect2.manytomanyview.ListBuilderFilterListViewMixin, BaseView):
    pass
