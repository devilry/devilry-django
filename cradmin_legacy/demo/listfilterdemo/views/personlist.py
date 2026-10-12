from cradmin_legacy import crapp
from cradmin_legacy.demo.listfilterdemo.models import Person
from cradmin_legacy.viewhelpers import listbuilderview
from cradmin_legacy.viewhelpers import listfilter


class OrderPersonsFilter(listfilter.django.single.select.AbstractOrderBy):
    def get_ordering_options(self):
        return [
            (
                "",
                {  # This will be the default sort order
                    "label": "Name",
                    "order_by": ["name"],
                },
            ),
            (
                "name_descending",
                {
                    "label": "Name (descending)",
                    "order_by": ["-name"],
                },
            ),
        ]


class PersonListView(listbuilderview.FilterListMixin, listbuilderview.View):
    model = Person

    def add_filterlist_items(self, filterlist):
        """
        Add the filters to the filterlist.
        """
        filterlist.append(
            listfilter.django.single.textinput.Search(
                slug="search", label="Search", label_is_screenreader_only=True, modelfields=["name"]
            )
        )
        filterlist.append(OrderPersonsFilter(slug="orderby", label="Order by"))
        filterlist.append(listfilter.django.single.select.NullDateTime(slug="banned_datetime", label="Banned time"))

    def get_filterlist_url(self, filters_string):
        """
        This is used by the filterlist to create URLs.
        """
        return self.request.cradmin_app.reverse_appurl("filter", kwargs={"filters_string": filters_string})

    def get_unfiltered_queryset_for_role(self, site):
        """
        Create the queryset, and apply the filters from the filterlist.
        """
        return Person.objects.filter(site=site)


class App(crapp.App):
    appurls = [
        crapp.Url(r"^$", PersonListView.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(r"^filter/(?P<filters_string>.+)?$", PersonListView.as_view(), name="filter"),
    ]
