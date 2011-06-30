.. _grade-plugins:


=============
Grade plugins
=============

A grade plugin is a way to plug-in custom grade-handling. We will explain how
to create a grade plugin by explaining the most simple grade plugin used in
Devilry, ``devilry.apps.grade_default``. ``grade_default`` simply allows for
any string between 1 and  15 characters to be used as a grade.


The model
#########

A grade plugin is simply a one-to-one relationship between
:class:`devilry.apps.core.models.Feedback` and a custom django-model defined by the
grade-plugin. This is the contents of *models.py*:

.. literalinclude:: /../devilry/apps/grade_default/models.py

As you can see, the model is a subclass of
:class:`devilry.gradeplugin.GradeModel`, which in turn is a subclass of
``django.db.Model``. ``GradeModel`` simply defines and documents some extra
functions.


The view
########

Next we have to create a view which examiners can use to give feedback using
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
:attr:`devilry.apps.core.gradeplugin.registry` explains all the details.


Grade plugin classes
####################

.. currentmodule:: devilry.apps.core.gradeplugin

.. automodule:: devilry.apps.core.gradeplugin
