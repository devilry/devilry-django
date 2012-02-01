from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

from devilry.apps.core.models import Delivery, Assignment, StaticFeedback
from registry import gradeeditor_registry


class Config(models.Model):
    """
    Stored by admins.

    .. attribute:: gradeeditorid

        A ``gradeeditorid`` that is used to get the
        :class:`devilry.apps.gradeeditors.registry.RegistryItem` for this
        config.

    .. attribute:: assignment

        The primary key. This means we have one config for each assignment.

    .. attribute:: config

        A text field where the config editor can store its data in any format
        it chooses. JSON is usually a good choice because of easy interraction
        with JavaScript.
    """
    gradeeditorid = models.SlugField()
    assignment = models.OneToOneField(Assignment, related_name='gradeeditor_config',
                                      primary_key=True)
    config = models.TextField(null=True, blank=True)

    def _get_gradeeditor(self):
        return gradeeditor_registry[self.gradeeditorid]

    def clean(self):
        """
        Gets a :class:`devilry.apps.gradeeditors.registry.RegistryItem` from
        the ``gradeeditor_registry`` in
        :mod:`devilry.apps.gradeeditor.registry`.

        Uses
        :meth:`devilry.apps.gradeeditors.registry.RegistryItem.validate_config`
        to validate the config before saving it.
        """
        try:
            config = self._get_gradeeditor()
        except KeyError, e:
            raise ValidationError('Invalid grade editor: {0}'.format(self.gradeeditorid))
        if self.config:
            config.validate_config(self.config)



def create_gradeconfig_for_assignment(sender, **kwargs):
    """
    Signal handler which is invoked when an Assignment is created.

    Create default grade Config for Assignment with ``config=''`` if the assignment
    has no grade Config.

    :param kwargs: Must have an *instance* key with an assignment object as value.
    """
    assignment = kwargs['instance']
    try:
        config = assignment.gradeeditor_config
    except Config.DoesNotExist:
        config = Config(assignment=assignment,
                        gradeeditorid=gradeeditor_registry.getdefaultkey(),
                        config='')
        config.save()

post_save.connect(create_gradeconfig_for_assignment,
                  sender=Assignment)


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
                                          related_name='gradeeditor_feedbackdraft',
                                          help_text='The StaticFeedback where this was published if this draft has been published.')

    def _get_config(self):
        return self.delivery.deadline.assignment_group.parentnode.gradeeditor_config

    def clean(self):
        if self.id == None: # If creating a new FeedbackDraft
            try:
                config = self._get_config()
            except Config.DoesNotExist:
                raise ValidationError(('Can not create feedback on delivery:{0} '
                                       'because its assignment does not have a '
                                       'gradeeditor_config.').format(self.delivery))
            else:
                gradeeditor = config._get_gradeeditor()
                gradeeditor.validate_draft(self.draft, config.config)
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
            _tmp_staticfeedback = self.to_staticfeedback()
            _tmp_staticfeedback.full_clean()
            _tmp_staticfeedback.save()
            self.staticfeedback = _tmp_staticfeedback # Note: We use _tmp_staticfeedback because if we need a variable in which to store the staticfeedback while we save it. We can not just save self.staticfeedback() because that would just create create a copy without actually setting self.staticfeedback to the newly saved value.
        super(FeedbackDraft, self).save(*args, **kwargs)

    def to_staticfeedback(self):
        """ Return a staticfeedback generated from self. """
        config = self._get_config()
        gradeeditor = config._get_gradeeditor()
        kwargs = gradeeditor.draft_to_staticfeedback_kwargs(self.draft, config.config)

        # Create StaticFeedback from kwargs. We copy by key instead of **kwargs to make sure we dont get anything extra.
        return StaticFeedback(is_passing_grade=kwargs['is_passing_grade'],
                              grade=kwargs['grade'],
                              points=kwargs['points'],
                              rendered_view=kwargs['rendered_view'],
                              delivery=self.delivery,
                              save_timestamp=None,
                              saved_by=self.saved_by)
