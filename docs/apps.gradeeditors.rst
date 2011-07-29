.. _apps.gradeeditors:


==================================================
:mod:`devilry.apps.gradeeditors` --- Grade editors
==================================================

**WARNING**: OUTDATED docs. This will be updated for the new *grade editors*.




The view
########

.. Next we have to create a view which examiners can use to give feedback using
    this plugin. To make grade-plugins as flexible as possible, the grade-plugin
    gets complete control of the view for the entire feedback. This means that the
    view has to create a complete view for creating a new
    :class:`devilry.apps.core.models.Feedback`. This is a lot of work, so we provide
    some :ref:`shortcuts <grade-plugins-feedback-view>` which makes
    it possible for our view to look a simple as this (*gradeviews.py*):

TODO: New example

..  .. literalinclude:: /../devilry/apps/grade_default/gradeviews.py


Register the plugin
###################

To make the plugin register itself when the server starts, you need to put
something like the following in ``devilry_plugin.py`` in you plugin (see
:ref:`plugins`):

TODO : New example.

.. .. literalinclude:: /../devilry/apps/grade_default/devilry_plugin.py

You can see that we register our *model* and our *view*. The API-docs for
:attr:`devilry.apps.gradeeditors.registry.gradeeditor_registry` explains all the details.


Grade editor classes
####################

.. currentmodule:: devilry.apps.gradeeditors.registry

.. automodule:: devilry.apps.gradeeditors.registry
