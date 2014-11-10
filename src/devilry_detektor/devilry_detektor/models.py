import json
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import detektor
import detektor.parseresult

from devilry.apps.core import models as coremodels


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

    def __unicode__(self):
        return u'DetektorAssignment#{} on {}'.format(self.id, self.assignment.get_path())


class DetektorDeliveryParseResult(models.Model, detektor.parseresult.ParseResult):
    """
    A Django model that implements the :class:`detektor.parseresult.ParseResult`
    interface.

    We store results from detektor parsing in this model, and read it from
    the database each time we need to compare.
    """
    detektorassignment = models.ForeignKey(DetektorAssignment, related_name='parseresults')
    delivery = models.ForeignKey(coremodels.Delivery)
    language = models.CharField(max_length=255, db_index=True)

    operators_string = models.TextField()
    keywords_string = models.TextField()
    number_of_operators = models.IntegerField()
    number_of_keywords = models.IntegerField()
    operators_and_keywords_string = models.TextField()
    normalized_sourcecode = models.TextField(null=True, blank=True)
    parsed_functions_json = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = [('delivery', 'language')]

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
        if not hasattr(self, '_parsed_functions'):
            if self.parsed_functions_json is None:
                self._parsed_functions = []
            else:
                parsed_functions = json.loads(self.parsed_functions_json)
                self._parsed_functions = [
                    detektor.parseresult.UneditableParseResult(parsed_function_dict)\
                    for parsed_function_dict in parsed_functions]
        return self._parsed_functions

    def get_parsed_functions(self):
        return self._get_parsed_functions()

    def from_parseresult(self, parseresult):
        data = parseresult.serialize_as_dict()
        self.operators_string = data['operators_string']
        self.keywords_string = data['keywords_string']
        self.number_of_operators = data['number_of_operators']
        self.number_of_keywords = data['number_of_keywords']
        self.operators_and_keywords_string = data['operators_and_keywords_string']
        self.normalized_sourcecode = data['normalized_sourcecode']
        if data['parsed_functions']:
            self.parsed_functions_json = json.dumps(data['parsed_functions'])
        else:
            self.parsed_functions_json = None


def expire_view_cache(view_name, args=[], kwargs={}, namespace=None, key_prefix=None, method="GET"):
    """
    This function allows you to invalidate any view-level cache.
        view_name: view function you wish to invalidate or it's named url pattern
        args: any arguments passed to the view function
        kwargs: any keyword arguments passed to the view function
        namepace: optioal, if an application namespace is needed
        key prefix: for the @cache_page decorator for the function (if any)

    See: https://gist.github.com/dpnova/1223933
    """
    from django.core.urlresolvers import reverse
    from django.http import HttpRequest
    from django.utils.cache import get_cache_key
    from django.core.cache import cache
    from django.conf import settings
    # create a fake request object
    request = HttpRequest()
    request.method = method
    if settings.USE_I18N:
        request.LANGUAGE_CODE = settings.LANGUAGE_CODE
    # Loookup the request path:
    if namespace:
        view_name = namespace + ":" + view_name
    request.path = reverse(view_name, args=args, kwargs=kwargs)
    # get cache key, expire if the cached item exists:
    key = get_cache_key(request, key_prefix=key_prefix)
    if key:
        if cache.get(key):
            cache.set(key, None, 0)
        return True
    return False


@receiver(post_save, sender=DetektorAssignment)
def on_detektorassignment_post_save(sender, instance, **kwargs):
    print
    print "*" * 70
    print
    print 'Clear cache'
    print
    print "*" * 70
    print

    expire_view_cache('devilry_detektor_admin_assignmentassembly',
                      kwargs={'assignmentid': instance.assignment_id})
