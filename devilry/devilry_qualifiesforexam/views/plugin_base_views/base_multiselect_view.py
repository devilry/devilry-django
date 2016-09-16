# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
from django import forms
from django.contrib import messages

# CrAdmin imports
from django_cradmin.viewhelpers import multiselect2
from django_cradmin.viewhelpers import multiselect2view


class SelectedQualificationForm(forms.Form):
    """
    Abstract form class.

    Subclass this and provide the desired functionality.
    """
    class Meta:
        abstract = True

    qualification_modelclass = None
    invalid_qualification_item_message = 'Invalid qualification items was selected.'

    #: The items selected as ModelMultipleChoiceField.
    #: If some or all items should be selected by defualt, override this.
    selected_items = forms.ModelMultipleChoiceField(

        # No items are selectable by default.
        queryset=None,

        # Used if the object to select for some reason does
        # not exist(has been deleted or altered in some way)
        error_messages={
            'invalid_choice': invalid_qualification_item_message,
        }
    )


class SelectedQualificationItem(multiselect2.selected_item_renderer.SelectedItem):
    """
    The selected item from the list.

    This can be subclassed if needed.
    """
    def get_title(self):
        """
        Get the title of an item.

        Returns:
            str: :obj:`.SelectedQualificationItem.value`s string representation.
        """
        return self.value


class SelectableQualificationItemValue(multiselect2.listbuilder_itemvalues.ItemValue):
    """

    """
    selected_item_renderer_class = SelectedQualificationItem

    def get_inputfield_name(self):
        return 'selected_items'

    def get_title(self):
        return self.value

    def get_description(self):
        return ''


class QualificationItemTargetRenderer(multiselect2.target_renderer.Target):
    """
    Target renderer for selected items.

    Provides default descriptions for target status when no items are selected, items are selected
    and the submit button text.

    Subclass this if changes to these labels need to be made.
    """

    #: The selected item as it is shown when selected.
    #: By default this is :class:`.SelectedQualificationItem`.
    selected_target_renderer = SelectedQualificationItem

    #: A descriptive name for the items selected.
    #: This defaults to 'items', but should be overridden with a
    #: name describing the exact items that are selectable.
    descriptive_item_name = 'items'

    def get_submit_button_text(self):
        """
        Returns:
            str: The text that should be shown on the submit button.
        """
        return 'Submit selected {}'.format(self.descriptive_item_name)

    def get_with_items_title(self):
        """
        Returns:
            str: The text that should be shown when items are selected.
        """
        return 'Selected {}'.format(self.descriptive_item_name)

    def get_without_items_text(self):
        """
        Returns:
            str: The text that should be shown when no items are selected.
        """
        return 'No {} selected'.format(self.descriptive_item_name)


class QualificationItemListView(multiselect2view.ListbuilderView):
    """
    Abstract multiselect view.

    This view must be subclassed and attribute ``model`` must be set.
    """
    class Meta:
        abstract = True

    #: The model represented as a selectable item.
    #: This attribute has to be set in the subclass.
    model = None
    value_renderer_class = SelectableQualificationItemValue

    def get_queryset_for_role(self, role):
        """
        Get a queryset all the objects for :obj:`.QualificationItemListView.model`

        This can be be customized with a call to super, and the
        filtering needed.

        Args:
            role: The cradmin role.

        Returns:
            QuerySet: queryset of from specified model.
        """
        return self.model.objects.all()

    def get_target_renderer_class(self):
        """
        Get the target renderer class.

        If a subclass of :class:`.QualificationItemTargetRenderer` is created, override
        this method by returning the subclass.

        Returns:
            QualificationItemTargetRenderer: Or subclass of this.
        """
        return QualificationItemTargetRenderer

    def get_form_class(self):
        """
        Get a subclass of :class:`.SelectedQualificationForm'.

        Must be implemented in subclass.

        Raises:
            NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError

    def get_form_kwargs(self):
        kwargs = super(QualificationItemListView, self).get_form_kwargs()
        kwargs['selectable_items_queryset'] = self.get_queryset_for_role(self.request.cradmin_role)
        # print 'get_form_kwargs'
        # print kwargs['selectable_items_queryset']
        return kwargs

    def form_valid(self, form):
        qualification_item_names = ['"{}"'.format(item) for item in form.cleaned_data['selected_items']]
        messages.success(
            self.request,
            'POST OK. Selected: {}'.format(', '.join(qualification_item_names)))
        return None
