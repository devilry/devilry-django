============================================
:mod:`devilry_qualifiesforexam`
============================================

.. py:currentmodule:: devilry_qualifiesforexam.models

Database models, APIs and UI for qualifying students for final exams.


.. _qualifiesforexam-uiworkflow:

#######################################################
UI workflow
#######################################################
How users are qualified for final exam i plugin-based. The subject/period admin is taken through
a wizard with the following steps/pages:

1. If no configuration exists for the period:
       List the title and description of each plugin (see :ref:`qualifiesforexam-plugins` below),
       and let the user select the plugin they want to use. The selection is stored in
       :attr:`QualifiesForFinalExamPeriodStatus.plugin`.
   If a configuration exists for the period:
       Show the overview of the semester (basically the same as the preview described as page 3 below).
       Includes a button to change the configuration. Clicking this button will show the list
       of plugins, just like when no configuration exists, with the previously used plugin
       selected. The *change*-button is only available on active periods.
2. Completely controlled by the plugin. May be more than one page if that should be needed by
   the plugin. The plugin can also just redirect directly to the next page if it does not require
   any input from the user. We supply a footer with save and back buttons that should be the same
   for all plugins.
3. Preview the results with the option to save or go back to the previous page.



.. _qualifiesforexam-plugins:

#######################################################
Plugins
#######################################################
A plugin is a regular Django app.


Registering an app as a qualifiesforexam plugin
===============================================
Add something like the following to ``yourapp/devilry_plugin.py``::

    from devilry_qualifiesforexam.registry import qualifiesforexam_plugins
    from django.core.urlresolvers import reverse
    from django.utils.translation import ugettext_lazy as _

    qualifiesforexam_plugins.add(
        id='myapp',
        url=reverse('myapp-myplugin'), # The url of the view to use for step/page 2 in the workflow
        title=_('My plugin'),
        description=_('Does <strong>this</strong> and <em>that</em>.')
    )



Configure available plugins
===========================
Available plugins are configured in ``settings.DEVILRY_QUALIFIESFOREXAM_PLUGINS``, which is
a list of plugin ids. Note that the apps containing the plugin must also be in ``settings.INSTALLED_APPS``.
The plugins are shown in listed order on page 1 of the wizard described in the
:ref:`qualifiesforexam-uiworkflow`.

.. note::
    You can safely remove plugins from ``settings.DEVILRY_QUALIFIESFOREXAM_PLUGINS``.
    They will simply not be available in the list of plugins in the
    :ref:`qualifiesforexam-uiworkflow`.




#######################################################
Plugins shipped with Devilry
#######################################################

``devilry_qualifiesforexam_approved``
==========================================
TODO





.. _qualifiesforexam-models:

#######################################################
Database models
#######################################################

.. py:class:: QualifiesForFinalExam

    .. py:attribute:: relatedstudent

        Database one-to-one relation to :class:`devilry.apps.core.models.RelatedStudent`.

    .. py:attribute:: qualifies

        Boolean database field telling


.. py:class:: QualifiesForFinalExamPeriodStatus

    Every time the admin updates qualifies-for-exam on a period, we save new object of this
    database model.

    This gives us a history of changes, and it makes it possible for subject/period admins
    to communicate simple information to whoever it is that is responsible for handling
    examinations.


    .. py:attribute:: period

        Database foreign key to the :class:`devilry.apps.core.models.Period` that the
        status is for.

    .. py:attribute:: status

        Database char field that accepts the following values:
    
        - ``ready`` is used to indicate the the entire period is ready for export/use.
        - ``almostready`` is used to indicate that the period is almost ready for export/use, and
          that the exceptions are explained in the :attr:`.message`.
        - ``notready`` is used to indicate that the period has no useful data yet. This is typically
          only used when the period used to be *ready* or *almostready*, but had to be retracted
          for a reason explained in the status

    .. py:attribute:: createtime

        Database datetime field where we store when we added the status.

    .. py:attribute:: message

        Database field with an optional message about the status change.

    .. py:attribute:: user

        Database foreign key to the user that made the status change.

    .. py:attribute:: plugin

        Database char field that stores the id of the plugin (see :ref:`qualifiesforexam-plugins`)
        that was used to change the status.