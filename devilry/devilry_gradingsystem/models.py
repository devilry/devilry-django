from datetime import datetime
import os
import uuid
from django.core.urlresolvers import reverse
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from devilry.apps.core.models import Delivery
from devilry.apps.core.models import StaticFeedback
from devilry.apps.core.models import StaticFeedbackFileAttachment


class FeedbackDraft(models.Model):
    """
    Created by examiners when they provide feedback. A StaticFeedback is
    automatically created when a FeedbackDraft is published.
    """
    DEFAULT_FEEDBACKTEXT_EDITOR = 'devilry-markdown'

    delivery = models.ForeignKey(Delivery, related_name='devilry_gradingsystem_feedbackdraft_set')
    feedbacktext_editor = models.CharField(
        default=DEFAULT_FEEDBACKTEXT_EDITOR,
        max_length='20',
        choices=(
            ('devilry-markdown', 'Markdown editor'),
            ('wysiwyg-html', 'WYSIWYG html')
        ))
    feedbacktext_raw = models.TextField(
        blank=True, null=True)
    feedbacktext_html = models.TextField(
        blank=True, null=True)
    points = models.PositiveIntegerField(
        blank=False, null=False)
    saved_by = models.ForeignKey(User, related_name='devilry_gradingsystem_feedbackdraft_set')
    published = models.BooleanField(
        default=False,
        help_text=('Has this draft been published as a StaticFeedback? '
                   'Setting this to true on create automatically creates a StaticFeedback.'))
    staticfeedback = models.OneToOneField(
        StaticFeedback,
        blank=True, null=True,
        related_name='devilry_gradingsystem_feedbackdraft_set',
        help_text='The StaticFeedback where this was published if this draft has been published.')
    save_timestamp = models.DateTimeField(
        blank=False, null=False,
        help_text='Time when this feedback was saved. Since FeedbackDraft is immutable, this never changes.')

    def clean(self):
        if self.id is None:  # If creating a new FeedbackDraft
            if not self.published:
                self.staticfeedback = None  # We should NEVER set staticfeedback if published is not True
        else:
            raise ValidationError('FeedbackDraft is immutable (it can not be changed).')
        if self.published and self.staticfeedack is None:
            raise ValidationError('Published FeedbackDraft requires a StaticFeedback.')

    def save(self, *args, **kwargs):
        self.save_timestamp = datetime.now()
        super(FeedbackDraft, self).save(*args, **kwargs)

    def to_staticfeedback(self, assignment=None):
        return StaticFeedback.from_points(
            self.points,
            assignment=assignment,
            delivery=self.delivery,
            rendered_view=self.feedbacktext_html,
            saved_by=self.saved_by)

    class Meta:
        ordering = ['-save_timestamp']


def feedback_draft_file_upload_to(instance, filename):
    extension = os.path.splitext(filename)[1]
    return u'devilry_gradingsystem/feedbackdraftfile/{deliveryid}/{uuid}{extension}'.format(
        deliveryid=instance.delivery_id,
        uuid=str(uuid.uuid1()),
        extension=extension)


class FeedbackDraftFile(models.Model):
    """
    A file that is part of the current draft.

    Unlike :class:`.FeedbackDraft`, we only keep one copy of the files.
    """
    delivery = models.ForeignKey(Delivery, related_name='+')
    saved_by = models.ForeignKey(User, related_name='+')

    #: The original filename.
    filename = models.TextField(blank=False, null=False)

    #: The uploaded file.
    file = models.FileField(
        upload_to=feedback_draft_file_upload_to
    )

    def get_download_url(self):
        return reverse('devilry_gradingsystem_feedbackdraftfile', kwargs={
            'pk': self.pk,
            'asciifilename': self.get_ascii_filename()
        })

    def __unicode__(self):
        return u'FeedbackDraftFile#{} by user#{} on delivery#{}'.format(
            self.pk, self.saved_by_id, self.delivery_id)

    def to_staticfeedbackfileattachment(self, staticfeedback):
        """
        Create a :class:`devilry.apps.core.models.StaticFeedbackFileAttachment`
        from this FeedbackDraftFile.
        """
        fileattachment = StaticFeedbackFileAttachment(
            staticfeedback=staticfeedback, filename=self.filename)
        fileattachment.file.save(self.filename, self.file)
        return fileattachment

    def get_ascii_filename(self):
        return self.filename.encode('ascii', 'ignore')

    class Meta:
        ordering = ['filename']  # Should have the same ordering as StaticFeedbackFileAttachment
