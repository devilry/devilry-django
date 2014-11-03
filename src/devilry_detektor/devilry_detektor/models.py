import json
from django.db import models
from django.contrib.auth.models import User
import detektor
import detektor.parseresult

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


class DetektorDeliveryParseResult(models.Model, detektor.parseresult.ParseResult):
    """
    A Django model that implements the :class:`detektor.parseresult.ParseResult`
    interface.

    We store results from detektor parsing in this model, and read it from
    the database each time we need to compare.
    """
    detektorassignment = models.ForeignKey(DetektorAssignment)
    delivery = models.OneToOneField(coremodels.Delivery)

    operators_string = models.TextField()
    keywords_string = models.TextField()
    number_of_operators = models.IntegerField()
    number_of_keywords = models.IntegerField()
    operators_and_keywords_string = models.TextField()
    normalized_sourcecode = models.TextField()
    parsed_functions_json = models.TextField()

    def get_codeblocktype(self):
        return 'program'

    def get_label(self):
        return unicode(self.delivery)

    def get_operators_string(self):
        return self.operators_string

    def get_keywords_string(self):
        return self.keywords_string

    def get_number_of_operators(self):
        return self.number_of_operators

    def get_number_of_keywords(self):
        return self.number_of_keywords

    def get_operators_and_keywords_string(self):
        return self.operators_and_keywords_string

    def get_normalized_sourcecode(self):
        return self.normalized_sourcecode

    def _get_parsed_functions(self):
        if hasattr(self, '_parsed_functions'):
            parsed_functions = json.loads(self.parsed_functions_json)
            self._parsed_functions = [
                detektor.parseresult.UneditableParseResult(parsed_function_dict)\
                for parsed_function_dict in parsed_functions]
        return self._parsed_functions

    def get_parsed_functions(self):
        return self._get_parsed_functions()
