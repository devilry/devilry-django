import json
from xml.sax.saxutils import quoteattr

from django import forms
from django.contrib import messages
from django.db import models
from django.views.generic.edit import FormMixin

from cradmin_legacy.viewhelpers import listbuilderview
from cradmin_legacy.viewhelpers import multiselect2


class ViewMixin(FormMixin):
    """
    Multiselect2 view mixin. Must be mixin in before any Django View subclass.

    This is typically used with a Django ListView or TemplateView.
    """

    def get_target_renderer_class(self):
        """
        Get the target renderer class.

        Must return :class:`cradmin_legacy.viewhelpers.multiselect2.target_renderer.Target`
        or a subclass of that class.

        Defaults to returning :class:`cradmin_legacy.viewhelpers.multiselect2.target_renderer.Target`.
        """
        return multiselect2.target_renderer.Target

    def get_target_renderer_kwargs(self):
        """
        Get keywork arguments for the class returned
        by :meth:`.get_target_renderer_class`

        You should call ``super()`` when overriding this method
        to get any default kwargs provided by this method.
        """
        return {"form": self.get_form(form_class=self.get_form_class())}

    def get_target_renderer(self):
        """
        Get the target renderer object.

        Must return an object of :class:`cradmin_legacy.viewhelpers.multiselect2.target_renderer.Target`
        or a subclass of that class.

        .. note:: You normally do not override this method, but instead
            you override :meth:`.get_target_renderer_kwargs` and
            :meth:`.get_target_renderer_class`.
        """
        return self.get_target_renderer_class()(**self.get_target_renderer_kwargs())

    def __get_target_renderer(self):
        if not hasattr(self, "_target_renderer"):
            self._target_renderer = self.get_target_renderer()
        return self._target_renderer

    def get_selectall_directive_dict(self):
        """
        Get options for the ``cradmin-legacy-multiselect2-selectall`` angularjs
        directive.

        Returns:
            dict: With options for the directive.
        """
        return {
            "target_dom_id": self.__get_target_renderer().get_dom_id(),
        }

    def get_selectall_directive_json(self):
        """
        Returns:
            str: The return value of :meth:`.get_select_directive_dict`
            as a json encoded and xml attribute encoded string.
        """
        return quoteattr(json.dumps(self.get_selectall_directive_dict()))

    def __has_initially_selected_items(self):
        return len(self._get_selected_values_set()) > 0

    def __select_all_button_should_be_shown(self, context):
        page_obj = context.get("page_obj", None)
        if page_obj and page_obj.number != 1:
            return False
        return self.select_all_is_allowed()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["target_renderer"] = self.__get_target_renderer()
        context["selectall_directive_json"] = self.get_selectall_directive_json()
        context["select_all_button_should_be_shown"] = self.__select_all_button_should_be_shown(context=context)

        # When we have initial items, we reload page1 after selecting the initially
        # selected items. This is because we need to load the items to select them,
        # but we do not want the initial selection to affect any further paging
        # and filtering on the page.
        context["must_reload_page1_on_load"] = self.__has_initially_selected_items()
        return context

    def is_initially_selected(self, value):
        """
        Should the provided value be selected on load?

        You normally do not need to override this. Override:

        - :meth:`.get_inititially_selected_queryset`
        - and for very rare cases, override :meth:`.get_postrequest_selected_queryset`.

        Args:
            value: A value in the listbuilder list (an object in the queryset).

        Returns:
            bool: If the provided value should be selected on load, return ``True``,
            otherwise return ``False``. Defaults to ``False`` if you do not overrie
            this method.
        """
        return value in self._get_selected_values_set()

    def __is_bgreplaced(self):
        return self.request.GET.get("cradmin-bgreplaced", "false") == "true"

    def __value_is_selected(self, value):
        if self.__is_bgreplaced():
            return False
        else:
            return self.is_initially_selected(value=value)

    def make_value_and_frame_renderer_kwargs(self, value):
        """
        This method is called by :meth:`.get_listbuilder_list_kwargs` (below)
        to create kwargs for our value and frame renderers.
        """
        return {"is_selected": self.__value_is_selected(value=value)}

    def get_value_and_frame_renderer_kwargs(self):
        """
        We return a callable here. This callable is used to create
        individual kwargs for each value in the list.
        """
        return self.make_value_and_frame_renderer_kwargs

    def get_selected_items_form_attribute(self):
        """
        Get the form attribute that contains the selected items.

        Defaults to ``"selected_items"``, so you need to override this
        if you use something else in your form.
        """
        return "selected_items"

    def get_selectable_items_queryset(self):
        if hasattr(self, "get_unfiltered_queryset_for_role"):
            queryset = self.get_unfiltered_queryset_for_role(role=self.request.cradmin_role)
        else:
            queryset = self.get_queryset_for_role(role=self.request.cradmin_role)
        return queryset

    def __make_selected_items_form_class(self):
        selected_items_form_attribute = self.get_selected_items_form_attribute()
        selectable_items_queryset = self.get_selectable_items_queryset()

        class SelectedItemsForm(forms.Form):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.fields[selected_items_form_attribute] = forms.ModelMultipleChoiceField(
                    queryset=selectable_items_queryset
                )

        return SelectedItemsForm

    def get_postrequest_selected_queryset(self):
        """
        Get a QuerySet of the items that was selected on POST.

        If the form attribute where you set your selected items is not
        named ``"selected_items"``, you have to override :meth:`.get_selected_items_form_attribute`.

        You normally do not need to override this method.

        Optionally, you can override both :meth:`.form_invalid_init` and :meth:`.form_invalid`
        to disable autoselect of the items that was selected before post.
        """
        form_class = self.__make_selected_items_form_class()
        form = form_class(self.request.POST)
        if form.is_valid():
            selected_items_form_attribute = self.get_selected_items_form_attribute()
            return form.cleaned_data[selected_items_form_attribute]
        else:
            return self.model.objects.none()

    def get_inititially_selected_queryset(self):
        """
        Get queryset of initially selected items.

        Defaults to ``self.model.object.none()``, and you should override this
        if you want to select any objects on load.
        """
        return self.model.objects.none()

    def get_selected_values_queryset(self):
        if self.request.method == "POST":
            queryset = self.get_postrequest_selected_queryset()
        elif self.__is_bgreplaced():
            queryset = self.model.objects.none()
        else:
            queryset = self.get_inititially_selected_queryset()
        return queryset

    def _get_selected_values_set(self):
        if not hasattr(self, "_selected_values_set"):
            self._selected_values_set = set(self.get_selected_values_queryset())
        return self._selected_values_set

    def form_invalid_init(self, form):
        """
        Called before ``form_invalid()`` to initialize the required attributes for
        ``form_invalid()``.

        If you provide a custom ``form_invalid``-method that does not re-render
        the page (I.E.: returns a HttpResponseRedirect with an error message),
        you can override this method
        """
        self.object_list = self.get_queryset()

    def form_invalid_add_global_errormessages(self, form):
        """
        Called before ``form_invalid()`` to handle adding global error messages.

        We add any error messages in the :meth:`.get_selected_items_form_attribute`
        field as a Django messages framework error message by default.

        Args:
            form: The form object.
        """
        if self.get_selected_items_form_attribute() in form.errors:
            errormessages = form.errors[self.get_selected_items_form_attribute()]
            for errormessage in errormessages:
                messages.error(self.request, errormessage)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            self.form_invalid_init(form=form)
            self.form_invalid_add_global_errormessages(form=form)
            return self.form_invalid(form)

    def get_number_of_extra_items_in_page_with_initially_selected(self):
        """
        Get the number of extra items to add to ``paginate_by`` when
        loading initial items, and the number of initial items is larger
        than the page size.

        This is used in :meth:`.paginate_by`.

        Defaults to ``10``.
        """
        return 10

    def get_paginate_by_handling_initially_selected(self, paginate_by):
        number_of_initially_selected_items = len(self._get_selected_values_set())
        extra_items = self.get_number_of_extra_items_in_page_with_initially_selected()
        if paginate_by < (number_of_initially_selected_items + extra_items):
            # Initially select only works if the selected items is loaded,
            # so we need to override page size to ensure they are included
            paginate_by = number_of_initially_selected_items + extra_items
        return paginate_by

    def disable_paging_requested(self):
        """
        If this returns ``True``, we disable paging.

        The default implementation disables paging if ``disablePaging=true`` is
        in the querystring (in ``request.GET``).
        """
        return self.request.GET.get("disablePaging", "false") == "true"

    def get_default_paginate_by(self, queryset):
        """
        Get the default page size.

        See :meth:`.paginate_by` for more details.
        """
        return self.paginate_by

    def get_paginate_by(self, queryset):
        """
        Returns the page size. You should normally override :meth:`.get_default_paginate_by`
        instead of this method.

        .. warning:: Be very careful if you override this. We handle
            the following cases by default, and if you just return a static value
            here, these cases will be broken:

            - If you have initially selected items, eighter because you override
              :meth:`.get_inititially_selected_queryset` or because posting the form
              fails, and you need to re-select all the items that was posted, we ensure
              that the initial page size is the number of selected items + the number
              returned by :meth:`.get_number_of_extra_items_in_page_with_initially_selected`.
              This is handled so that the page is first loaded with this custom page size,
              and then the list is reloaded by an angularjs directive with page size set
              to :meth:`.get_default_paginate_by`.
            - If you have ``disablePaging=true`` in the querystring of the request, which
              is what the default "Select all" button does, we disable paging.

            This means that you should override:

            - :meth:`.get_default_paginate_by`
            - :meth:`.get_number_of_extra_items_in_page_with_initially_selected`

            in almost all cases unless you want to make a major rewrite of all methods
            related to handling the cases listed above.
        """
        if self.disable_paging_requested():
            return None
        paginate_by = self.get_default_paginate_by(queryset=queryset)
        if paginate_by and self.__has_initially_selected_items():
            paginate_by = self.get_paginate_by_handling_initially_selected(paginate_by=paginate_by)
        return paginate_by

    def __order_queryset(self, queryset):
        """
        Order the queryset. We have to order the queryset so that
        the initially selected items is included on the first page (if pagination is enabled).

        We do this by annotating the queryset with ``cradmin_multiselect2_ordering``,
        and inserting that as the first order_by argument.
        """
        if self.get_paginate_by(queryset) and self.request.method == "POST" and self.__has_initially_selected_items():
            current_order_by = list(queryset.query.order_by)
            whenqueries = []
            max_index = 0
            for index, value in enumerate(self.get_selected_values_queryset().order_by(*current_order_by)):
                whenqueries.append(models.When(pk=value.pk, then=models.Value(index)))
                max_index = index
            queryset = queryset.annotate(
                cradmin_multiselect2_ordering=models.Case(
                    *whenqueries, default=max_index + 1, output_field=models.IntegerField()
                )
            )
            order_by = ["cradmin_multiselect2_ordering"]
            order_by.extend(current_order_by)
            queryset = queryset.order_by(*order_by)
        return queryset

    def get_queryset(self):
        queryset = super().get_queryset().distinct()
        queryset = self.get_selected_values_queryset().distinct() | queryset
        queryset = queryset.distinct()
        return self.__order_queryset(queryset)

    def get_total_number_of_items_in_queryset(self):
        """
        Get the total number of items in the queryset.

        .. note:: This is cached in ``self._total_number_of_items_in_queryset`` on
            first call, so calling this multiple times for a single request
            will only require one database query.
        """
        if not hasattr(self, "_total_number_of_items_in_queryset"):
            self._total_number_of_items_in_queryset = self.get_queryset().count()
        return self._total_number_of_items_in_queryset

    def get_select_all_max_items(self):
        """
        The maximum number of items to allow for select all button.

        If this returns a value other than ``None``, we do not render the "Select all" button,
        if the number of total items available for "Select all" is more than this number.

        Defaults to ``1500``.
        """
        return 1500

    def select_all_is_allowed(self):
        """
        Checks if "Select all" is allowed, and returns ``True`` if it is.

        You normally do not need to override this, override :meth:`.get_select_all_max_items`
        instead. The only reason to override this is if you want to disable "Select all"
        completely, in which case you return ``False``.
        """
        select_all_max_items = self.get_select_all_max_items()
        if select_all_max_items is None:
            return True
        else:
            return select_all_max_items > self.get_total_number_of_items_in_queryset()


class ListbuilderView(ViewMixin, listbuilderview.View):
    """
    Multiselect2 listbuilder view.
    """

    template_name = "cradmin_legacy/viewhelpers/multiselect2view/listbuilderview.django.html"
    value_renderer_class = multiselect2.listbuilder_itemvalues.ItemValue


class ListbuilderFilterView(ViewMixin, listbuilderview.FilterListMixin, listbuilderview.View):
    """
    Multiselect2 listbuilder view with filters.
    """

    template_name = "cradmin_legacy/viewhelpers/multiselect2view/listbuilderfilterview.django.html"
    value_renderer_class = multiselect2.listbuilder_itemvalues.ItemValue

    def get_filterlist_template_name(self):
        return self.template_name
