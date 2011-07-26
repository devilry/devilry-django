from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

from devilry.apps.core.models import Delivery, Assignment, StaticFeedback
from registry import gradeeditor_registry


class Config(models.Model):
    """
    Stored by admins.
    """
    gradeeditorid = models.SlugField()
    assignment = models.OneToOneField(Assignment, related_name='gradeeditor_config')
    config = models.TextField()


class FeedbackDraft(models.Model):
    """
    Stored by examiners.
    """
    delivery = models.ForeignKey(Delivery)
    draft = models.TextField()
    save_timestamp = models.DateTimeField(auto_now=True, blank=False, null=False,
                                          help_text='Time when this feedback was saved. Since FeedbackDraft '
                                                    'is immutable, this never changes.')
    saved_by = models.ForeignKey(User)
    published = models.BooleanField(default=False,
                                    help_text='Has this draft been published as a StaticFeedback? Setting this to true on create automatically creates a StaticFeedback.')
    staticfeedback = models.OneToOneField(StaticFeedback, blank=True, null=True,
                                          help_text='The StaticFeedback where this was published if this draft has been published.')

    def clean(self):
        if self.id == None: # If creating a new FeedbackDraft
            if not self.published:
                self.staticfeedback = None # We should NEVER set staticfeedback if published is not True
            assignment = self.delivery.deadline.assignment_group.parentnode
            try:
                config = assignment.gradeeditor_config
            except Config.DoesNotExist:
                raise ValidationError(('Can not create feedback on delivery:{0} '
                                       'because assignment:{1} does not have a '
                                       'gradeeditor_config.').format(self.delivery,
                                                                     assignment))
            self.staticfeedback = self._to_staticfeedback()
            self.staticfeedback.full_clean()
        else:
            raise ValidationError('FeedbackDraft is immutable (it can not be changed).')

    def save(self, *args, **kwargs):
        super(FeedbackDraft, self).save(*args, **kwargs)
        if self.staticfeedback:
            self.staticfeedback.save()

    def _to_staticfeedback(self):
        config = self.delivery.deadline.assignment_group.parentnode.gradeeditor_config
        print config



#def handle_feedbackdraft_delete(sender, **kwargs):
    #feedbackdraft = kwargs['instance']
    #if feedbackdraft.published:
        #feedbackdraft._publish()


#from django.db.models.signals import post_save
#post_save.connect(handle_feedbackdraft_delete,
                  #sender=FeedbackDraft)
