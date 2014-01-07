from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from devilry.apps.core.models import Delivery
from devilry.apps.core.models import StaticFeedback


class FeedbackDraft(models.Model):
    """
    Created by examiners when they provide feedback. A StaticFeedback is
    automatically created when a FeedbackDraft is published.
    """
    delivery = models.ForeignKey(Delivery, related_name='devilry_gradingsystem_feedbackdraft_set')
    feedbacktext_raw = models.TextField()
    feedbacktext_html = models.TextField()
    save_timestamp = models.DateTimeField(
        auto_now=True, blank=False, null=False,
        help_text='Time when this feedback was saved. Since FeedbackDraft is immutable, this never changes.')
    saved_by = models.ForeignKey(User, related_name='devilry_gradingsystem_feedbackdraft_set')
    published = models.BooleanField(default=False,
        help_text='Has this draft been published as a StaticFeedback? Setting this to true on create automatically creates a StaticFeedback.')
    staticfeedback = models.OneToOneField(StaticFeedback,
        blank=True, null=True,
        related_name='devilry_gradingsystem_feedbackdraft_set',
        help_text='The StaticFeedback where this was published if this draft has been published.')

    def _get_config(self):
        return self.delivery.deadline.assignment_group.parentnode.devilry_gradingsystem_config

    def clean(self):
        if self.id == None: # If creating a new FeedbackDraft
            if not self.published:
                self.staticfeedback = None # We should NEVER set staticfeedback if published is not True
        else:
            raise ValidationError('FeedbackDraft is immutable (it can not be changed).')

    def save(self, *args, **kwargs):
        """
        Save the draft and optionally a :class:`devilry.core.models.StaticFeedback`
        in the database. The ``StaticFeedback`` is only saved if
        ``self.publish`` is ``True``.

        Uses :meth:`to_staticfeedback` to create the staticfeedback.
        """
        if self.published:
            tmp_staticfeedback = self.to_staticfeedback()
            tmp_staticfeedback.full_clean()
            tmp_staticfeedback.save()
            self.staticfeedback = tmp_staticfeedback # Note: We use tmp_staticfeedback because if we need a variable in which to store the staticfeedback while we save it. We can not just save self.staticfeedback() because that would just create create a copy without actually setting self.staticfeedback to the newly saved value.
        super(FeedbackDraft, self).save(*args, **kwargs)

    def to_staticfeedback(self):
        """ Return a staticfeedback generated from self. """
        # gradeeditor = config._get_gradeeditor()
        # kwargs = gradeeditor.draft_to_staticfeedback_kwargs(self.draft, config.config)

        # Create StaticFeedback from kwargs. We copy by key instead of **kwargs to make sure we dont get anything extra.
        # return StaticFeedback(is_passing_grade=kwargs['is_passing_grade'],
        #                       grade=kwargs['grade'],
        #                       points=kwargs['points'],
        #                       rendered_view=kwargs['rendered_view'],
        #                       delivery=self.delivery,
        #                       save_timestamp=None,
        #                       saved_by=self.saved_by)
