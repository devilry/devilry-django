# -*- coding: utf-8 -*-


# Django imports
from django import forms
from django.http import HttpResponseRedirect

# CrAdmin imports
from django.utils.translation import gettext_lazy
from cradmin_legacy.viewhelpers import multiselect2
from cradmin_legacy.viewhelpers import multiselect2view

# Devilry imports
from devilry.devilry_qualifiesforexam import models as status_models
from devilry.apps.core import models as core_models

import json

class QualifiedForExamPluginViewMixin(object):
    plugintypeid = None

    def get_plugintypeid(self):
        return self.plugintypeid


class SelectedQualificationForm(forms.Form):
    """
    Subclass this if extra fields needs to be added.
    """
    qualification_modelclass = core_models.Assignment
    invalid_qualification_item_message = gettext_lazy('Invalid qualification items was selected.')

    #: The items selected as ModelMultipleChoiceField.
    #: If some or all items should be selected by default, override this.
    selected_items = forms.ModelMultipleChoiceField(

        # No items are selectable by default.
        queryset=None,

        # Used if the object to select for some reason does
        # not exist(has been deleted or altered in some way)
        error_messages={
            'invalid_choice': invalid_qualification_item_message,
        }
    )

    def __init__(self, *args, **kwargs):
        selectable_qualification_items_queryset = kwargs.pop('selectable_items_queryset')
        super(SelectedQualificationForm, self).__init__(*args, **kwargs)
        self.fields['selected_items'].queryset = selectable_qualification_items_queryset


class SelectedQualificationItem(multiselect2.selected_item_renderer.SelectedItem):
    """
    The selected item from the list.

    This can be subclassed if needed.
    """
    def get_title(self):
        """
        Get the title of an item.

        Returns:
            str: :obj:`.SelectedQualificationItem.value` string representation.
        """
        return self.value


class SelectableQualificationItemValue(multiselect2.listbuilder_itemvalues.ItemValue):
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
    descriptive_item_name = gettext_lazy('assignments')

    def get_submit_button_text(self):
        """
        Returns:
            str: The text that should be shown on the submit button.
        """
        return gettext_lazy('Submit selected %(what)s') % {'what': self.descriptive_item_name}

    def get_with_items_title(self):
        """
        Returns:
            str: The text that should be shown when items are selected.
        """
        return gettext_lazy('Selected %(what)s') % {'what': self.descriptive_item_name}

    def get_without_items_text(self):
        """
        Returns:
            str: The text that should be shown when no items are selected.
        """
        return gettext_lazy('No %(what)s selected') % {'what': self.descriptive_item_name}


class QualificationItemListView(multiselect2view.ListbuilderView, QualifiedForExamPluginViewMixin):
    """
    This class provides a basic multiselect preset.

    By default, this class uses :class:`~.devilry.devilry.apps.core.models.Assignment` as model. This
    means that this class lists all the ``Assignments`` for the ``Period`` as selectable items and all items
    are selected by default.

    If you only want to list ``Assignment`` as selectable items and no extra fields needs to be added to the form, just
    subclass this and override :meth:`~.get_period_result_collector_class`.

    Examples:

        Here is an example of a plugin view that uses ``Assignment`` as listing values and nothing else::

            from devilry.devilry_qualifiesforexam.views.plugin_base_views import base_multiselect_view
            from devilry.devilry_qualifiesforexam.views import plugin_mixin


            class PluginSelectAssignmentsView(base_multiselect_view.QualificationItemListView, plugin_mixin.PluginMixin):
                plugintypeid = 'devilry_qualifiesforexam_plugin_approved.plugin_select_assignments'

                def get_period_result_collector_class(self):
                    return some_result_collector_for_the_plugin

        Here is an example that uses ``Assignment`` as selectable items but an extra field is added, to
        achieve this, the base form and target renderer must be subclassed::

            from devilry.devilry_qualifiesforexam.views.plugin_base_views import base_multiselect_view
            from devilry.devilry_qualifiesforexam_plugin_points import resultscollector
            from devilry.devilry_qualifiesforexam.views import plugin_mixin


            class PluginSelectAssignmentsAndPoints(base_multiselect_view.SelectedQualificationForm):
                min_points_to_achieve = forms.IntegerField(
                        min_value=0,
                        required=False,
                )


            class WithPointsFormDataTargetRenderer(base_multiselect_view.QualificationItemTargetRenderer):
                def get_field_layout(self):
                    return [
                        'min_points_to_achieve'
                    ]


            class PluginSelectAssignmentsAndPointsView(base_multiselect_view.QualificationItemListView, plugin_mixin.PluginMixin):
                plugintypeid = 'devilry_qualifiesforexam_plugin_approved.plugin_select_assignments_and_points'

                def get_period_result_collector_class(self):
                    return resultscollector.PeriodResultSetCollector

                def get_form_class(self):
                    return PluginSelectAssignmentsAndPoints

                def get_target_renderer_class(self):
                    return WithPointsFormDataTargetRenderer

    """
    class Meta:
        abstract = True

    #: The model represented as a selectable item.
    model = core_models.Assignment
    value_renderer_class = SelectableQualificationItemValue

    def dispatch(self, request, *args, **kwargs):
        """
        Check if a :class:`~.devilry_qualifiesforexam.models.Status` with ``status`` set to
        ``ready`` exists for the period. If it exists, redirect to the final export view.
        """
        period = self.request.cradmin_role
        status = status_models.Status.objects.get_last_status_in_period(period=period)
        if status and status.status == status_models.Status.READY:
            return HttpResponseRedirect(str(self.request.cradmin_app.reverse_appurl(
                viewname='show-status',
                kwargs={
                    'roleid': self.request.cradmin_role.id,
                    'statusid': status.id
                }
            )))
        return super(QualificationItemListView, self).dispatch(request, *args, **kwargs)

    def get_queryset_for_role(self, role):
        """
        Get a queryset of all the objects for the :obj:`.QualificationItemListView.model` .

        This can be be customized with a call to super, and the
        filtering needed.

        Args:
            role: The cradmin_role(Period).

        Returns:
            QuerySet: queryset of from specified model.
        """
        queryset = self.model.objects.all()
        return queryset.filter(parentnode__id=role.id)

    def get_inititially_selected_queryset(self):
        return self.get_queryset_for_role(self.request.cradmin_role)

    def get_target_renderer_class(self):
        """
        Get the target renderer class.

        If a subclass of :class:`.QualificationItemTargetRenderer` is created, override
        this method by returning the subclass.

        Returns:
            :class:`~.QualificationItemTargetRenderer`
        """
        return QualificationItemTargetRenderer

    def get_form_class(self):
        """
        Get a subclass of :class:`.SelectedQualificationForm`.

        Must be implemented in subclass.

        Raises:
            NotImplementedError: If not implemented by subclass.
        """
        return SelectedQualificationForm

    def get_period_result_collector_class(self):
        """
        Must be implemented by subclass if needed.

        Returns:
            A subclass of :class:`devilry.devilry_qualifiesforexam.pluginshelper.PeriodResultsCollector`

        Raises:
            NotImplementedError
        """
        raise NotImplementedError

    def get_qualifying_itemids(self, posted_form):
        """
        Get the ID of the items that qualify.

        Args:
            posted_form: The posted form containing the items selected.

        Returns:
            List of ``self.model.id`` that were selected.
        """
        return [item.id for item in posted_form.cleaned_data['selected_items']]

    def get_form_kwargs(self):
        kwargs = super(QualificationItemListView, self).get_form_kwargs()
        kwargs['selectable_items_queryset'] = self.get_queryset_for_role(self.request.cradmin_role)
        return kwargs

    def form_valid(self, form):
        """
        Provides some basic functionality. If custom fields are added to the form,
        this function must be overridden in subclass to handle the posted data.

        Args:
            form: Posted form with ids of selected items.
        """
        # Collect qualifying Assignment IDs
        qualifying_assignmentids = self.get_qualifying_itemids(posted_form=form)

        # Collect ids for relatedstudents that qualify
        collector_class = self.get_period_result_collector_class()
        passing_relatedstudentids = collector_class(
                period=self.request.cradmin_role,
                qualifying_assignment_ids=qualifying_assignmentids
        ).get_relatedstudents_that_qualify_for_exam()

        # Attach collected data to session.
        self.request.session['passing_relatedstudentids'] = passing_relatedstudentids
        self.request.session['plugintypeid'] = self.get_plugintypeid()
        print(json.dumps(qualifying_assignmentids))
        self.request.session['plugindata'] = json.dumps(qualifying_assignmentids)
        
        return HttpResponseRedirect(str(self.request.cradmin_app.reverse_appurl('preview')))
