from datetime import datetime
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy
from django import forms
from crispy_forms import layout
from django.views.generic import TemplateView
from django.utils import timezone

from cradmin_legacy.viewhelpers import objecttable
from cradmin_legacy.viewhelpers import listfilter
from cradmin_legacy.viewhelpers import create
from cradmin_legacy.viewhelpers import update
from cradmin_legacy.viewhelpers import delete
from cradmin_legacy.viewhelpers import multiselect
from cradmin_legacy import crapp
from cradmin_legacy.acemarkdown.widgets import AceMarkdownWidget
from cradmin_legacy.crispylayouts import PrimarySubmit
from cradmin_legacy.apps.cradmin_imagearchive.models import ArchiveImage
from cradmin_legacy.demo.webdemo.models import Page
from cradmin_legacy.widgets import filewidgets
from cradmin_legacy.widgets.modelchoice import ModelChoiceWidget
from cradmin_legacy.widgets.datetimepicker import DateTimePickerWidget, DatePickerWidget


class TitleColumn(objecttable.MultiActionColumn):
    modelfield = "title"

    def get_buttons(self, obj):
        return [
            objecttable.Button(label="Edit", url=self.reverse_appurl("edit", args=[obj.id])),
            objecttable.PagePreviewButton(label="View", url=self.reverse_appurl("preview", args=[obj.id])),
            objecttable.Button(
                label="Delete", url=self.reverse_appurl("delete", args=[obj.id]), buttonclass="btn btn-danger btn-sm"
            ),
        ]


class PagesQuerySetForRoleMixin:
    """
    Used by listing, update and delete view to ensure
    that only pages that the current role has access to
    is available.
    """

    def get_queryset_for_role(self, site):
        return Page.objects.filter(site=site)


class ArchiveImagePreviewColumn(objecttable.ImagePreviewColumn):
    modelfield = "image"

    def render_value(self, obj):
        if obj.image:
            return obj.image.image
        else:
            return None


class IntroColumn(objecttable.TruncatecharsPlainTextColumn):
    modelfield = "intro"
    maxlength = 40
    allcells_css_classes = ["hidden-xs"]


class PagesListView(objecttable.FilterListMixin, PagesQuerySetForRoleMixin, objecttable.ObjectTableView):
    model = Page
    enable_previews = True
    columns = [
        ArchiveImagePreviewColumn,
        TitleColumn,
        IntroColumn,
    ]
    # filterlist_class = listfilter.lists.Horizontal

    def get_buttons(self):
        app = self.request.cradmin_app
        return [
            objecttable.Button(
                label=gettext_lazy("Create"), url=app.reverse_appurl("create"), buttonclass="btn btn-primary"
            ),
        ]

    def get_multiselect_actions(self):
        app = self.request.cradmin_app
        return [
            objecttable.MultiSelectAction(label=gettext_lazy("Edit"), url=app.reverse_appurl("multiedit")),
        ]

    # def get_filterlist_position(self):
    #     return 'left'
    # def get_label_is_screenreader_only_by_default(self):
    #     return True

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl("filter", kwargs={"filters_string": filters_string})

    def add_filterlist_items(self, filterlist):
        filterlist.append(
            listfilter.django.single.textinput.Search(
                slug="search", label="Search", label_is_screenreader_only=True, modelfields=["title"]
            )
        )
        filterlist.append(listfilter.django.single.select.IsNotNull(slug="image", label="Has image?"))
        filterlist.append(listfilter.django.single.select.DateTime(slug="publishing_time", label="Publishing time"))

    def get_unfiltered_queryset_for_role(self, site):
        return PagesQuerySetForRoleMixin.get_queryset_for_role(self, site=site)


class PageCreateUpdateMixin:
    model = Page
    roleid_field = "site"
    enable_modelchoicefield_support = True
    fields = ["title", "intro", "body", "image", "publishing_time", "unpublish_time", "attachment", "internal_notes"]

    def get_preview_url(self):
        return self.request.cradmin_app.reverse_appurl("preview")

    def _get_image_selectview_url(self):
        return self.request.cradmin_instance.reverse_url("imagearchive", "singleselect")

    def get_field_layout(self):
        return [
            layout.Div("title", css_class="cradmin-focusfield cradmin-focusfield-lg"),
            layout.Fieldset(
                "Image",
                "image",
            ),
            layout.Div("intro", css_class="cradmin-focusfield"),
            layout.Div("body", css_class="cradmin-focusfield"),
            layout.Fieldset("Advanced", "publishing_time", "unpublish_time", "attachment", "internal_notes"),
            # layout.Div(
            #     'publishing_time',
            #     'internal_notes',
            #     css_class='cradmin-globalfields'
            # ),
        ]

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        # form.fields['body'].widget = WysiHtmlTextArea(attrs={})
        form.fields["body"].widget = AceMarkdownWidget()
        preview = '<p class="text-muted">(No image selected)</p>'
        if self.object and self.object.image:
            preview = self.object.image.get_preview_html(request=self.request)
        form.fields["image"].widget = ModelChoiceWidget(
            queryset=ArchiveImage.objects.filter_owned_by_role(self.request.cradmin_role),
            preview=preview,
            selectview_url=self._get_image_selectview_url(),
        )
        form.fields["publishing_time"].widget = DateTimePickerWidget(
            # minimum_datetime=datetime(2014, 8, 14, 12, 30),
            minimum_datetime=timezone.now(),
            maximum_datetime=datetime(2030, 12, 5, 21, 40),
            required=False,
        )
        form.fields["unpublish_time"].widget = DatePickerWidget(no_value_preview_text="No date selected")
        # form.fields['unpublish_time'].widget = DateTimePickerWidget(
        #     no_value_preview_text='No date selected')
        form.fields["attachment"].widget = filewidgets.ImageWidget(request=self.request)
        # form.fields['attachment'].widget = filewidgets.FileWidget()
        return form


class PageCreateView(PageCreateUpdateMixin, create.CreateView):
    """
    View used to create new pages.
    """


class PageUpdateView(PagesQuerySetForRoleMixin, PageCreateUpdateMixin, update.UpdateView):
    """
    View used to create edit existing pages.
    """


class PreviewPageView(TemplateView):
    template_name = "webdemo/pages/preview.django.html"

    def __get_page(self):
        if self.kwargs["pk"] is None:
            return PageCreateView.get_preview_data(self.request)
        else:
            # NOTE: The queryset ensures only admins on the current site gains access.
            site = self.request.cradmin_role
            return get_object_or_404(Page.objects.filter(site=site), pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page"] = self.__get_page()
        return context


class PageDeleteView(PagesQuerySetForRoleMixin, delete.DeleteView):
    """
    View used to delete existing pages.
    """


class PageMultiEditForm(forms.Form):
    new_body = forms.CharField(label="New value for the page body", required=True, widget=forms.Textarea)


class PageMultiEditView(PagesQuerySetForRoleMixin, multiselect.MultiSelectFormView):
    form_class = PageMultiEditForm
    model = Page

    def get_buttons(self):
        return [PrimarySubmit("submit-save", gettext_lazy("Update text for selected pages"))]

    def get_field_layout(self):
        return [
            layout.Div("new_body", css_class="cradmin-focusfield cradmin-focusfield-screenheight"),
        ]

    def form_valid(self, form):
        self.selected_objects.update(body=form.cleaned_data["new_body"])
        return self.success_redirect_response()

    def get_initial(self):
        return {"new_body": "Write something here..."}


class App(crapp.App):
    appurls = [
        crapp.Url(r"^$", PagesListView.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(r"^filter/(?P<filters_string>.+)?$", PagesListView.as_view(), name="filter"),
        crapp.Url(r"^create$", PageCreateView.as_view(), name="create"),
        crapp.Url(r"^edit/(?P<pk>\d+)$", PageUpdateView.as_view(), name="edit"),
        crapp.Url(r"^preview/(?P<pk>\d+)?$", PreviewPageView.as_view(), name="preview"),
        crapp.Url(r"^delete/(?P<pk>\d+)$", PageDeleteView.as_view(), name="delete"),
        crapp.Url(r"^multiedit/$", PageMultiEditView.as_view(), name="multiedit"),
    ]
