.. _developer-howto-grade-plugins:


=============
Grade plugins
=============

A grade plugin is a way to plug-in custom grade-handling. We will explain how
to create a grade plugin by explaining the most simple grade plugin used in
Devilry, ``devilry.addons.grade_default``. ``grade_default`` simply allows for
any string between 1 and  15 characters to be used as a grade.


The model
#########

A grade plugin is simply a one-to-one relationship between
:class:`devilry.core.models.Feedback` and a custom django-model defined by the
grade-plugin. This is the contents of *models.py*:

.. literalinclude:: /../../devilry/addons/grade_default/models.py


Grade plugin classes
####################

.. currentmodule:: devilry.core.gradeplugin

.. automodule:: devilry.core.gradeplugin




Feedback-view
#############

.. currentmodule:: devilry.examiner.feedback_view

.. autoclass:: devilry.examiner.feedback_view
