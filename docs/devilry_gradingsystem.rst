################################################################################
:mod:`devilry_gradingsystem` --- The devilry grading system plugin architecture
################################################################################

.. warning:: Under development.

How we configure the grading system on an assignment
====================================================

#. Select a grading system plugin.
#. Configure the grading system plugin (plugins can opt out of this step by
   setting :obj:`~devilry_gradingsystem.pluginregistry.GradingSystemPluginInterface.requires_configuration`).
#. Configure the maximum number of points possible (plugins can opt out of this step by setting :obj:`~devilry_gradingsystem.pluginregistry.GradingSystemPluginInterface.sets_max_points_automatically`).
#. Choose how students are graded:
    - Passed failed
    - Raw points
    - Custom table
#. Configure required points to pass (plugins can opt out of this step by setting :obj:`~devilry_gradingsystem.pluginregistry.GradingSystemPluginInterface.sets_passing_grade_min_points_automatically`):
    - If ``raw-points`` or ``passed-failed``: Select a number of points between ``0`` and ``max_points``, including both ends.
    - If custom table: Select a grade from the table.
      


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
