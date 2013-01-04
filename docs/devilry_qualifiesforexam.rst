============================================
:mod:`devilry_qualifiesforexam`
============================================

Database models, APIs and UI for qualifying students for final exams.



Database models
###############

.. py:currentmodule:: devilry_qualifiesforexam.models

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