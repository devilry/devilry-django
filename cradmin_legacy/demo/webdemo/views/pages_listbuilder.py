from django.contrib.auth import get_user_model

from cradmin_legacy import crapp
from cradmin_legacy.demo.webdemo.models import Page, PageTag
from cradmin_legacy.demo.webdemo.views.pages import (
    PageCreateView,
    PageDeleteView,
    PagesQuerySetForRoleMixin,
    PageUpdateView,
    PreviewPageView,
)
from cradmin_legacy.viewhelpers import listbuilder, listbuilderview, listfilter
from cradmin_legacy.viewhelpers.listfilter.basefilters.single import abstractradio


class PageListItemValue(listbuilder.itemvalue.EditDeleteWithArchiveImageAndPreview):
    template_name = "webdemo/pages_listbuilder/pagelist-itemvalue.django.html"
    valuealias = "page"

    def get_archiveimage(self):
        return self.page.image

    def get_description(self):
        return self.page.intro


class OrderPagesFilter(listfilter.django.single.select.AbstractOrderBy):
    def get_ordering_options(self):
        return [
            (
                "",
                {
                    "label": "Publishing time (newest first)",
                    "order_by": ["-publishing_time"],
                },
            ),
            (
                "publishing_time_asc",
                {
                    "label": "Publishing time (oldest first)",
                    "order_by": ["publishing_time"],
                },
            ),
            (
                "title",
                {
                    "label": "Title",
                    "order_by": ["title"],
                },
            ),
        ]


class PageTagChecboxFilter(listfilter.django.multi.checkbox.RelatedModelOrFilter):
    def get_choices(self):
        return [(tag, tag) for tag in PageTag.objects.values_list("tag", flat=True).distinct()]

    def get_filter_attribute(self):
        return "tags__tag"


class PageTagRadioFilter(abstractradio.AbstractRadioFilter, listfilter.django.DjangoOrmFilterMixin):
    def get_choices(self):
        choices = [(tag, tag) for tag in PageTag.objects.values_list("tag", flat=True).distinct()]
        choices.insert(0, ("", "Ignore tags"))
        return choices

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value()
        if cleaned_value:
            queryobject = queryobject.filter(tags__tag=cleaned_value).distinct()
        return queryobject


class PageSubscriberFilter(listfilter.django.multi.checkbox.RelatedModelOrFilter):
    def get_choices(self):
        return [(user.username, str(user)) for user in get_user_model().objects.all()]

    def get_filter_attribute(self):
        return "subscribers__username"


class PagesListBuilderView(
    listbuilderview.FilterListMixin,
    PagesQuerySetForRoleMixin,
    listbuilderview.ViewCreateButtonMixin,
    listbuilderview.View,
):
    """
    Shows how to use listbuilderview with listfilter.
    """

    model = Page
    enable_previews = True
    # listbuilder_class = listbuilder.lists.FloatGridList
    value_renderer_class = PageListItemValue
    # filterlist_class = listfilter.lists.Horizontal

    # def get_filterlist_position(self):
    #     return 'left'
    # def get_label_is_screenreader_only_by_default(self):
    #     return True

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl("filter", kwargs={"filters_string": filters_string})

    def get_post_include_template(self):
        return "webdemo/pages_listbuilder/pagelist-post-include.django.html"

    def add_filterlist_items(self, filterlist):
        filterlist.append(
            listfilter.django.single.textinput.Search(
                slug="search", label="Search", label_is_screenreader_only=True, modelfields=["title"]
            )
        )
        filterlist.append(OrderPagesFilter(slug="orderby", label="Order by"))
        filterlist.append(listfilter.django.single.select.IsNotNull(slug="image", label="Has image?"))
        filterlist.append(listfilter.django.single.select.DateTime(slug="publishing_time", label="Publishing time"))
        # filterlist.append(PageTagChecboxFilter(
        #     slug='tags', label='Tag'))
        filterlist.append(PageTagRadioFilter(slug="tag", label="Tag"))
        filterlist.append(PageSubscriberFilter(slug="subscribers", label="Subscribers"))

    def get_unfiltered_queryset_for_role(self, site):
        return PagesQuerySetForRoleMixin.get_queryset_for_role(self, site=site).prefetch_related("tags")


class App(crapp.App):
    appurls = [
        crapp.Url(r"^$", PagesListBuilderView.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(r"^filter/(?P<filters_string>.+)?$", PagesListBuilderView.as_view(), name="filter"),
        crapp.Url(r"^create$", PageCreateView.as_view(), name="create"),
        crapp.Url(r"^edit/(?P<pk>\d+)$", PageUpdateView.as_view(), name="edit"),
        crapp.Url(r"^preview/(?P<pk>\d+)?$", PreviewPageView.as_view(), name="preview"),
        crapp.Url(r"^delete/(?P<pk>\d+)$", PageDeleteView.as_view(), name="delete"),
    ]
