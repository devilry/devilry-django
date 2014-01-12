################################################################################
:mod:`devilry_gradingsystem` --- The devilry grading system plugin architecture
################################################################################

.. warning:: Under development.

How we configure the grading system on an assignment
====================================================

1 - Select a grading system plugin.
-----------------------------------
User selects one of the plugins in the :obj:`devilry_gradingsystem.pluginregistry.gradingsystempluginregistry`.


2 - Configure the grading system plugin
---------------------------------------
User configures the grading system using the view pointed to by
:meth:`devilry_gradingsystem.pluginregistry.GradingSystemPluginInterface.get_configuration_url`.

.. note::

	This step is skipped unless the plugin has set
	:obj:`~devilry_gradingsystem.pluginregistry.GradingSystemPluginInterface.requires_configuration`
	to ``True``


3 - Configure the maximum number of points possible
---------------------------------------------------
User sets the maximum number of points possible.

.. note::

	Plugins can opt out of this step by setting
	:obj:`~devilry_gradingsystem.pluginregistry.GradingSystemPluginInterface.sets_max_points_automatically`
	to ``True``


4 - Choose how students are graded
----------------------------------
The user selects one of the possible values for :attr:`devilry.apps.core.models.Assignment.points_to_grade_mapper`):
    - Passed failed
    - Raw points
    - Custom table

5 - Configure the points to grade mapping table (only if ``custom-table``)
--------------------------------------------------------------------------
If the user selected ``custom-table``, they need to setup that table.


6 - Configure required points to pass
-------------------------------------
The user selects the number of points required to pass the assignment
(:attr:`devilry.apps.core.models.Assignment.passing_grade_min_points`).
How they do this depends on the ``points_to_grade_mapper``:

- If ``raw-points`` or ``passed-failed``: Select a number of points between ``0`` and ``max_points``, including both ends.
- If custom table: Select a grade from the table.    

.. note::

	Plugins can opt out of this step by setting :obj:`~devilry_gradingsystem.pluginregistry.GradingSystemPluginInterface.sets_passing_grade_min_points_automatically`)  


Creating a Plugin
=================
A grading system plugin must implement the
:class:`devilry_gradingsystem.pluginregistry.GradingSystemPluginInterface`, and
it must register the implemented class with 
:obj:`devilry_gradingsystem.pluginregistry.gradingsystempluginregistry`.

Please refer to one of the simple grading system plugins, such as
``devilry_gradingsystemplugin_points``, for a starting point for implementing
your own plugin.


API
===
.. automodule:: devilry_gradingsystem.pluginregistry
