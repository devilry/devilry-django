from crispy_forms import layout

from cradmin_legacy import crapp
from cradmin_legacy.demo.webdemo.views.pages import PageCreateView, PageDeleteView, PageUpdateView, PreviewPageView
from cradmin_legacy.demo.webdemo.views.pages_listbuilder import PagesListBuilderView


class FormUtilsPageUpdateView(PageUpdateView):
    fields = PageUpdateView.fields + ["starred"]

    def get_field_layout(self):
        return [
            layout.Div("title", css_class="cradmin-focusfield cradmin-focusfield-lg"),
            layout.Fieldset(
                "Image",
                "image",
            ),
            layout.Fieldset(
                "Starred?",
                layout.Field("starred", stuff_to_do="stuff"),
            ),
            layout.Div("intro", css_class="cradmin-focusfield"),
            layout.Div("body", css_class="cradmin-focusfield"),
            layout.Fieldset("Advanced", "publishing_time", "unpublish_time", "attachment", "internal_notes"),
        ]


class App(crapp.App):
    appurls = [
        crapp.Url(r"^$", PagesListBuilderView.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(r"^filter/(?P<filters_string>.+)?$", PagesListBuilderView.as_view(), name="filter"),
        crapp.Url(r"^create$", PageCreateView.as_view(), name="create"),
        crapp.Url(r"^edit/(?P<pk>\d+)$", FormUtilsPageUpdateView.as_view(), name="edit"),
        crapp.Url(r"^preview/(?P<pk>\d+)?$", PreviewPageView.as_view(), name="preview"),
        crapp.Url(r"^delete/(?P<pk>\d+)$", PageDeleteView.as_view(), name="delete"),
    ]
