from django.db import models
from django.contrib.auth.models import User

from devilry.apps.core import models as coremodels


# class DetektorAssignmentManager(models.Manager):


class DetektorAssignment(models.Model):
    """
    Tracks process of detektor running on an assignment.

    An object of this model is created the first time detektor
    processing is requested on an assignment. Subsequent processing
    requests re-use the same object.

    .. warning::
        This means that we do not allow parallel detektor processing
        on the same assignment.
    """
    assignment = models.OneToOneField(coremodels.Assignment)
    processing_started_datetime = models.DateTimeField(
        null=True, blank=True
    )
    processing_started_by = models.ForeignKey(
        User,
        null=True, blank=True)


class DetektorDelivery(models.Model):
    detektorassignment = models.ForeignKey(DetektorAssignment)
    delivery = models.OneToOneField(coremodels.Delivery)

    keywordstring = models.TextField()
    operatorstring = models.TextField()
    bigstring = models.TextField()
    bigstringhash = models.TextField()
    number_of_keywords = models.IntegerField()
    number_of_operators = models.IntegerField()
    list_of_functions = models.TextField()

    def __repr__(self):
        return u"""
Keywords: {}
Operators: {}
Bigstring: {}
Bigstringhash: {}
Number of keywords: {}
Number of operators: {}
Functions: {}""".format(
            self.keywordstring, self.operatorstring, self.bigstring,
            self.bigstringhash, self.number_of_keywords,
            self.number_of_operators, self.list_of_functions)
