# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
from django import forms
from django.contrib import messages
from django.http import HttpResponseRedirect

# CrAdmin imports
from django_cradmin.viewhelpers import multiselect2
from django_cradmin.viewhelpers import multiselect2view

# Devilry imports
from devilry.devilry_qualifiesforexam import models as status_models
from devilry.devilry_qualifiesforexam.models import QualifiesForFinalExam


def create_sessionkey(pluginsessionid):
    return 'qualifiesforexam-{}'.format(pluginsessionid)


def create_settings_sessionkey(pluginsessionid):
    return '{}-settings'.format(create_sessionkey(pluginsessionid))


class PreviewData(object):
    def __init__(self, passing_relatedstudentids):
        self.passing_relatedstudentids = passing_relatedstudentids

    def __str__(self):
        return 'PreviewData(passing_relatedstudentids={0!r})'.format(self.passing_relatedstudentids)

    def serialize(self):
        return {
            'passing_relatedstudentids': list(self.passing_relatedstudentids)
        }


class QualifiedForExamPluginViewMixin(object):
    pluginid = None

    def get_plugin_input_and_authenticate(self):
        self.period = self.request.cradmin_role
        self.pluginsessionid = self.request.session['pluginsessionid']

    def save_plugin_output(self, *args, **kwargs):
        self.request.session[create_sessionkey(self.pluginsessionid)] = PreviewData(*args, **kwargs).serialize()

    def save_settings_in_session(self, data):
        self.request.session[create_settings_sessionkey(self.pluginsessionid)] = data


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


class QualificationItemListView(multiselect2view.ListbuilderView, QualifiedForExamPluginViewMixin):
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

    def dispatch(self, request, *args, **kwargs):
        """
        Check if a :class:`~.devilry_qualifiesforexam.models.Status` with ``status`` set to
        ``ready`` exists for the period. If it exists, redirect to the final export view.
        """
        try:
            if status_models.Status.get_current_status(self.request.cradmin_role).status == status_models.Status.READY:
                # Currently raise Http404, add redirect to view later
                return HttpResponseRedirect(self.request.cradmin_app.reverse_appurl(
                    viewname='show-status',
                    kwargs={
                        'roleid': self.request.cradmin_role.id
                    }
                ))
        except status_models.Status.DoesNotExist:
            pass
        return super(QualificationItemListView, self).dispatch(request, *args, **kwargs)

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
        return kwargs

    def form_valid(self, form):
        qualification_item_ids = ['"{}:{}"'.format(item, item.id) for item in form.cleaned_data['selected_items']]
        messages.success(
            self.request,
            'POST OK. Selected: {}'.format(', '.join(qualification_item_ids)))
        return HttpResponseRedirect(self.request.cradmin_app.reverse_appurl('preview'))
