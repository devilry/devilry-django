from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models

from model_utils import Etag

class Candidate(models.Model, Etag):
    """
    .. attribute:: assignment_group

        The :class:`AssignmentGroup` where this groups belongs.

    .. attribute:: student

        A student (a foreign key to a User).

    .. attribute:: candidate_id

        A optional candidate id. This can be anything as long as it is not
        more than 30 characters. When the assignment is anonymous, this is
        the "name" shown to examiners instead of the username of the
        student.
    """

    class Meta:
        app_label = 'core'

    student = models.ForeignKey(User)
    assignment_group = models.ForeignKey('AssignmentGroup',
            related_name='candidates')

    # TODO unique within assignment as an option.
    candidate_id = models.CharField(max_length=30, blank=True, null=True)
    identifier = models.CharField(max_length=30)
    etag = models.DateTimeField(auto_now_add=True)

    def get_identifier(self):
        """
        Gives the identifier of the candidate. When the Assignment is anyonymous
        the candidate_id is returned. Else, the student name is returned. This
        method should always be used when retrieving the candidate identifier.
        """
        return self.identifier

    def __unicode__(self):
        return self.get_identifier()

    #TODO delete this?
    def save(self, *args, **kwargs):
        """Validate the assignment.

        Always call this before save()! Read about validation here:
        http://docs.djangoproject.com/en/dev/ref/models/instances/#id1

        Raises ValidationError if:

            - candidate id is empty on anonymous assignment.

        """
        if self.assignment_group.parentnode.anonymous:
            if not self.candidate_id:
                self.identifier = "candidate-id missing"
                # raise ValidationError(
                #     _("Candidate id cannot be empty when assignment
                #     is anonymous.)"))
            else:
                self.identifier = self.candidate_id
        else:
            self.identifier = self.student.username
        super(Candidate, self).save(*args, **kwargs)
