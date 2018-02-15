################################
:mod:`devilry_qualifiesforexam2`
################################

.. module:: devilry_qualifiesforexam

Database models, APIs and UI for qualifying students for final exams.


.. _qualifiesforexam-uiworkflow2:


***********
UI workflow
***********
Step 1, 3 and 4 is provided with the app, and step 2 is the actual "plugin" that's implemented, but more on that
further down in the `Creating a plugin`-section.

The numbered list below shows the preferable UI-workflow of a plugin.

1. Choose a plugin:
    List the title and description of each plugin and let the user select the plugin they want to use.
2. Plugin(this is usually the only part that needs to be implemented):
    This part is completely controlled by the plugin and may be more than one page if that should be needed by
    the plugin. This is where you crunch the data needed to display the final result.
3. Preview:
    Preview the results with the option to save or go back to the previous page.
4. Final state:
    When the preview is saved, a new view with the result should be shown. This view may "look" the same as the
    preview view. I most cases this will be a list of all students and their current status on whether they are
    qualified or not and status for each assignment.


Creating a plugin
=================

Using the already existing approved/not approved plugin as an example. The plugin shows a view where you can select the
assignments that needs to be approved for a student to qualify for the final exam.

A plugin can do whatever fits its purpose, just remember to follow the workflow above.

1: In you app create a view or views for the plugin. Using a multiselect view which lists all the assignments, and makes
it possible to either select or deselect each assignment.
You must create a form to be used, and the actual view to use by extending the needed classes provided in
``devilry.devilry_qualifiesforexam.views.plugin_base_views.base_multiselect_view``.

.. code-block:: python

    # Devilry imports
    from devilry.devilry_qualifiesforexam.views.plugin_base_views import base_multiselect_view
    from devilry.devilry_qualifiesforexam_plugin_approved import resultscollector
    from devilry.devilry_qualifiesforexam.views import plugin_mixin


    class PluginSelectAssignmentsView(base_multiselect_view.QualificationItemListView, plugin_mixin.PluginMixin):
        plugintypeid = 'devilry_qualifiesforexam_plugin_approved.plugin_select_assignments'

        def get_period_result_collector_class(self):
            return resultscollector.PeriodResultSetCollector


2: As you can see, we have defined a function `get_period_result_collector_class` in the class defined in step 1.
If you need to base the qualification status of a student on the achievements on assignments, you will need to
create a class for your plugin that extends ``devilry.devilry_qualifiesforexam.pluginhelpers.PeriodResultSet``
(as we need to do in this example).

.. code-block:: python

    # Devilry imports
    from devilry.devilry_qualifiesforexam.pluginhelpers import PeriodResultsCollector


    class PeriodResultSetCollector(PeriodResultsCollector):
        """
        A subset of assignments are evaluated for the period.
        """
        def student_qualifies_for_exam(self, aggregated_relstudentinfo):
            for assignmentid, groupfeedbacksetlist in aggregated_relstudentinfo.assignments.iteritems():
                if assignmentid in self.qualifying_assignment_ids or len(self.qualifying_assignment_ids) == 0:
                    feedbackset = groupfeedbacksetlist.get_feedbackset_with_most_points()
                    if not feedbackset:
                        return False
                    elif feedbackset.grading_points < feedbackset.group.parentnode.passing_grade_min_points:
                        return False
            return True


3: In your app, create a plugin.py file.
Inside the `plugin.py` create a class that extends
``devilry.devilry_qualifiesforexam.plugintyperegistry.PluginType``.
This defines the plugin you just created the view logic for in step 1.

.. code-block:: python

   from devilry.devilry_qualifiesforexam.plugintyperegistry import PluginType
   from .views import select_assignment

   class SelectAssignmentsPlugin(PluginType):
       plugintypeid = 'your_app_name.plugin_pluginname'
       human_readable_name = 'Select assignments'
       description = 'Some description of what the plugins does.'

       def get_plugin_view_class(self):
           return select_assignment.PluginSelectAssignmentsView


4: Register the plugin with the devilry_qualifiesforexam app by creating an apps.py file and load the plugin to the
registry when the app is loaded.

.. code-block:: python

    from django.apps import AppConfig


    class DevilryQualifiesForExamAppConfig(AppConfig):
        name = 'devilry.devilry_qualifiesforexam_plugin_approved'
        verbose_name = 'Devilry qualifies for exam plugin approved'

        def ready(self):
            from devilry.devilry_qualifiesforexam import plugintyperegistry
            from . import plugin
            plugintyperegistry.Registry.get_instance().add(plugin.SelectAssignmentsPlugin)


*************
Datamodel API
*************

.. currentmodule:: devilry.devilry_qualifiesforexam

.. automodule:: devilry.devilry_qualifiesforexam.models
    :members:



*********
Views API
*********

.. currentmodule:: devilry.devilry_group.qualifiesforexam

.. automodule:: devilry.devilry_qualifiesforexam.views.plugin_base_views.base_multiselect_view
    :members:
