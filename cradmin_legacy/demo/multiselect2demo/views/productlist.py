from django import forms
from django.contrib import messages
from django.shortcuts import redirect
from django.template import defaultfilters

from cradmin_legacy import crapp
from cradmin_legacy.demo.multiselect2demo.models import Product
from cradmin_legacy.viewhelpers import listfilter
from cradmin_legacy.viewhelpers import multiselect2
from cradmin_legacy.viewhelpers import multiselect2view


class SelectedProductsForm(forms.Form):
    """
    The form we use for validation and selected items extractions
    when the user submits their selection.

    It is just a plain Django form (can also be a ModelForm). You
    just have to make sure that the name of the form field (``selected_items``)
    matches the value returned by ``get_inputfield_name()`` in the
    ``SelectableProductItemValue`` class.
    """

    invalid_selected_items_message = "Invalid products was selected, please try again."
    selected_items = forms.ModelMultipleChoiceField(
        # No products selectable by default - we override this in __init__()
        queryset=Product.objects.none(),
        # This is not required for this example, but if your queryset for
        # selected items depends on data that can change (be deleted, made unavailable for
        # selection, ...), and thus make selection invalid, you should include a message
        # like this. You can try this out if you try to select an item in the demo
        # views, and delete the items (using the superuser UI) before submitting your
        # selection.
        error_messages={
            "invalid_choice": invalid_selected_items_message,
        },
    )

    def __init__(self, *args, **kwargs):
        selectable_items_queryset = kwargs.pop("selectable_items_queryset")
        super().__init__(*args, **kwargs)
        self.fields["selected_items"].queryset = selectable_items_queryset


class SelectedProductItem(multiselect2.selected_item_renderer.SelectedItem):
    """
    Define how selected items are rendered.

    You do not have to create this class - you can also just use
    the default value for the ``selected_item_renderer_class``
    You can just use the default value from
    ``multiselect2.listbuilder_itemvalues.ItemValue.selected_item_renderer_class``

    This only scratches the surface of all the options you have for
    how selected items are rendered. See
    :class:`cradmin_legacy.viewhelpers.multiselect2.selected_item_renderer.SelectedItem`
    for more details.
    """

    valuealias = "product"

    def get_title(self):
        return self.product.name


class SelectableProductItemValue(multiselect2.listbuilder_itemvalues.ItemValue):
    """
    Define how selectable items are rendered.

    You do not have to create this class - you can also just use
    :class:`cradmin_legacy.viewhelpers.multiselect2.listbuilder_itemvalues.ItemValue`
    directly if the defaults from that class suites your needs.

    This only scratches the surface of all the options you have for
    how selectable items are rendered. See
    :class:`cradmin_legacy.viewhelpers.multiselect2.listbuilder_itemvalues.ItemValue`
    for more details.
    """

    valuealias = "product"

    # You do not need to override this - the default works in most cases!
    selected_item_renderer_class = SelectedProductItem

    def get_inputfield_name(self):
        return "selected_items"

    def get_title(self):
        return self.product.name

    def get_description(self):
        return defaultfilters.truncatechars(self.product.description, 150)


class ProductTargetRenderer(multiselect2.target_renderer.Target):
    """
    Define how to render the box containing selected items.

    You do not have to create this class - you can also just use
    :class:`cradmin_legacy.viewhelpers.multiselect2.target_renderer.Target`
    directly if the defaults from that class suites your needs.

    This only scratches the surface of all the options you have for
    how the selected items box is rendered. See
    :class:`cradmin_legacy.viewhelpers.multiselect2.target_renderer.Target`
    for more details.
    """

    def get_with_items_title(self):
        return "Selected products:"

    def get_submit_button_text(self):
        return "Do some really awesomely cool stuff with products"

    def get_without_items_text(self):
        return "Nothing selected"


###########################################
#
# A very simple demo
#
###########################################


class ProductListView(multiselect2view.ListbuilderView):
    """
    A very simple example of a multiselect2 view.

    It could be simplified further since the following is optional:

    - You do not have to override ``value_renderer_class``.
    - You do not have to override ``get_target_renderer_class``.
    """

    model = Product
    value_renderer_class = SelectableProductItemValue
    paginate_by = 20

    def get_queryset_for_role(self, role):
        return Product.objects.all().order_by("name")

    def get_target_renderer_class(self):
        return ProductTargetRenderer

    #
    #
    # Handling the POST request is just like in a normal Django FormView.
    # The form is not used for GET requests, so the methods below
    # are just for handling POST requests (when users submit their selection).
    #
    #

    def get_form_class(self):
        return SelectedProductsForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["selectable_items_queryset"] = Product.objects.all()
        return kwargs

    def form_valid(self, form):
        productnames = [f'"{product.name}"' for product in form.cleaned_data["selected_items"]]
        messages.success(self.request, "POST OK. Selected: {}".format(", ".join(productnames)))
        return redirect(self.request.get_full_path())


###########################################
#
# With filters demo
#
###########################################


class FilteredProductListView(multiselect2view.ListbuilderFilterView):
    """
    This view is just like ProductListView except that it adds filters!
    """

    model = Product
    value_renderer_class = SelectableProductItemValue
    paginate_by = 20

    def add_filterlist_items(self, filterlist):
        filterlist.append(
            listfilter.django.single.textinput.Search(
                slug="search", label="Search", label_is_screenreader_only=True, modelfields=["name", "description"]
            )
        )

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl("withfilters", kwargs={"filters_string": filters_string})

    def get_unfiltered_queryset_for_role(self, role):
        return Product.objects.all().order_by("name")

    def get_target_renderer_class(self):
        return ProductTargetRenderer

    #
    #
    # Handling the POST request is just like in a normal Django FormView.
    # The form is not used for GET requests, so the methods below
    # are just for handling POST requests (when users submit their selection).
    #
    #

    def get_form_class(self):
        return SelectedProductsForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["selectable_items_queryset"] = Product.objects.all()
        return kwargs

    def form_valid(self, form):
        productnames = [f'"{product.name}"' for product in form.cleaned_data["selected_items"]]
        messages.success(self.request, "POST OK. Selected: {}".format(", ".join(productnames)))
        return redirect(self.request.get_full_path())


###########################################
#
# Select on load demo
#
###########################################


class ProductListViewSelectOnLoad(ProductListView):
    """
    Extends :class:`.ProductListView` to show how to select items when the
    view loads.
    """

    def get_inititially_selected_queryset(self):
        """
        Select all products that contains ``"sock"`` in their name on load.
        """
        return Product.objects.filter(name__icontains="sock")


###########################################
#
# With extra form data demo
#
###########################################


class SelectedProductsAndMoreForm(SelectedProductsForm):
    """
    We add an couple of extra required fields (age and tag) to :class:`.SelectedProductsForm`
    for this demo, to show that form validation works.
    """

    age = forms.CharField(required=True)
    tag = forms.MultipleChoiceField(
        required=True,
        choices=[
            ("booring", "Booring"),
            ("cool", "Cool"),
            ("awesome", "Awesome"),
        ],
        widget=forms.CheckboxSelectMultiple(),
    )


class WithExtraFormDataTargetRenderer(ProductTargetRenderer):
    """
    We have to add the ``age`` and ``tag`` fields to the target renderer.
    """

    def get_field_layout(self):
        return [
            "age",
            "tag",
        ]


class ProductListViewWithExtraFormData(FilteredProductListView):
    """
    Extends :class:`.ProductListView` to set the form with
    the ``age`` field, and the target renderer that includes
    the ``age`` field in the rendered form.
    """

    # paginate_by = 2

    # def get_select_all_max_items(self):
    #     return 3

    def get_form_class(self):
        return SelectedProductsAndMoreForm

    def get_target_renderer_class(self):
        return WithExtraFormDataTargetRenderer

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl("extra-form-data", kwargs={"filters_string": filters_string})

    # def get_inititially_selected_queryset(self):
    #     return Product.objects.filter(name__icontains='sock')

    def form_valid(self, form):
        messages.success(self.request, f"POST OK. Data: {form.cleaned_data!r}")
        return redirect(self.request.get_full_path())


###############################################
#
# Create an app with the views
#
###############################################


class App(crapp.App):
    appurls = [
        crapp.Url(r"^$", ProductListView.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(r"^with-filters/(?P<filters_string>.+)?$", FilteredProductListView.as_view(), name="withfilters"),
        crapp.Url(r"^select-on-load$", ProductListViewSelectOnLoad.as_view(), name="select-on-load"),
        crapp.Url(
            r"^extra-form-data/(?P<filters_string>.+)?$",
            ProductListViewWithExtraFormData.as_view(),
            name="extra-form-data",
        ),
    ]
