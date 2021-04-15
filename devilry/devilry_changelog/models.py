from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy
from devilry.apps.core.models import Assignment


class AbstractChangeLogItem(models.Model):
    class Meta:
        abstract = True

    #: Value for :obj:`~AbstractChangeLogItem.status` when the change is in progress.
    #: Only used for background tasks.
    STATUS_IN_PROGRESS = 'in-progress'

    #: Value for :obj:`~AbstractChangeLogItem.status` when the change failed.
    #: Only used for background tasks.
    STATUS_FAILED = 'failed'

    #: Value for :obj:`~AbstractChangeLogItem.status` when the change failed.
    STATUS_FINISHED = 'finished'

    #: The user that made the change.
    #: Can be ``None``, and it is set to ``None`` if a user is deleted.
    #: It is also typically set to ``None`` for changes made via system
    #: scripts.
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL,
                             null=True, blank=True)

    #: The status of the change. One of:
    #:
    #: - :obj:`.AbstractChangeLogItem.STATUS_IN_PROGRESS`
    #: - :obj:`.AbstractChangeLogItem.STATUS_FAILED`
    #: - :obj:`.AbstractChangeLogItem.STATUS_FINISHED`
    status = models.CharField(
        max_length=15,
        default=STATUS_FINISHED,
        choices=(
            (STATUS_IN_PROGRESS, gettext_lazy('in progress')),
            (STATUS_FAILED, gettext_lazy('failed')),
            (STATUS_FINISHED, gettext_lazy('finished')),
        )
    )

    #: The action performed.
    #: Identifies what was changed. This is always overridden in subclasses
    #: to provide a CharField with explicit choices.
    actions = None


class AssignmentChangeLogItem(AbstractChangeLogItem):
    ACTIONS = {
        'update-anonymous-ids': gettext_lazy('Update all candidate IDs and anonymous IDs.'),
        # 'change-publishing-time': gettext_lazy(''),
        # 'change-first-deadline': gettext_lazy(''),
    }

    actions = models.CharField(
        max_length=50,
        choices=list(ACTIONS.items())
    )
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
