"""
.. attribute:: gradeeditor_registry

    A :class:`Registry`-object.
"""
import json
import re
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

class ConfigValidationError(ValidationError):
    """
    Raised when :meth:`RegistryItem.validate_config` fails to validate the
    configstring.
    """

class DraftValidationError(ValidationError):
    """
    Raised when :meth:`RegistryItem.validate_draft` fails to validate the
    draftstring.
    """


class ShortFormatValidationError(ValidationError):
    """
    Raised when :meth:`.ShortFormat.validate` fails.
    """


class ShortFormatWidgets(object):
    STRING = 'string'
    BOOL = 'bool'
    NUM_OF_TOTAL = 'num-of-total'


class ShortFormat(object):
    widget = ShortFormatWidgets.STRING

    @classmethod
    def validate(cls, config, value):
        """
        Validate the given shortformat.

        :param config: A :class:`devilry.apps.gradeeditors.models.Config` object.
        """
        raise NotImplementedError()

    @classmethod
    def to_staticfeedback_kwargs(cls, config, value):
        """
        Convert ``value`` into a dictionary of keyword arguments for StaticFeedback.

        :param config: A :class:`devilry.apps.gradeeditors.models.Config` object.
        :param value: The value. This is already validated by :meth:`.validate` when
            sent to this method.

        :return:
            The returned dict should only contain the following keys:

                - is_passing_grade
                - grade
                - points
        """
        raise NotImplementedError()

    @classmethod
    def format_feedback(cls, config, feedback):
        """
        Format the given feedback on a format that is parsable by this ShortFormat.

        :param config: A :class:`devilry.apps.gradeeditors.models.Config` object.
        :param feedback: A :class:`devilry.apps.core.models.StaticFeedback`.
        :return: A string with the formatted feedback. The returned value must validate with
            :meth:`.validate`.
        """
        raise NotImplementedError()

    @classmethod
    def shorthelp(cls, config):
        """
        Get a short help for this shortformat. Can be more than 40 chars, but it should be
        understandable if we ellipsis the string at 40 chars (I.E.: cut the string and suffix with
        ``...``)
        :param config: A :class:`devilry.apps.gradeeditors.models.Config` object.
        """
        raise NotImplementedError()


class ShortFormatNumOfTotalBase(ShortFormat):
    widget = ShortFormatWidgets.NUM_OF_TOTAL

    @classmethod
    def validate(cls, config, value):
        if not value.isdigit():
            raise ShortFormatValidationError(_('Must be a number.'))

    @classmethod
    def get_value_as_number(cls, value):
        """
        Parse the value string and return it as a number.
        """
        return int(value)



class RegistryItem(object):
    """
    Information about a grade plugin.

    The attributes documented below are required.

    .. attribute:: gradeeditorid

        A unique string for this editor. If two editors with the same
        gradeeditorid is registered, an exception will be raised on load time.

    .. attribute:: title

        A short title for the grade editor.

    .. attribute:: description

        A longer description of the grade editor.

    .. attribute:: config_editor_url

        The URL to the config editor.

    .. attribute:: draft_editor_url

        The URL to the draft editor.

    .. attribute:: shortformat

        An optional :class:`.ShortFormat` for this plugin. If no shortformat is defined,
        the plugin will not be usable in places that require shortformat.
    """
    shortformat = None

    def __str__(self):
        return self.title

    @classmethod
    def validate_config(cls, configstring):
        """
        Validate ``configstring`` and raise :exc:`ConfigValidationError` if it
        does not validate.
        """
        raise NotImplementedError('This grade plugin does not support configuration')

    @classmethod
    def validate_draft(cls, draftstring):
        """
        Validate ``draftstring`` and raise :exc:`DraftValidationError` if the validation fails.
        """
        raise NotImplementedError()

    @classmethod
    def draft_to_staticfeedback_kwargs(cls, draftstring, configstring):
        """
        Convert ``draftstring`` into a dictionary of keyword arguments for StaticFeedback.

        :param draftstring: The draft as a string. Will usually be encoded in a structured format like XML or JSON.
        :param configstring: The grade editor config as a string. Will usually be encoded in a structured format like XML or JSON.

        :return:
            The returned dict should only contain the following keys:

                - is_passing_grade
                - grade
                - points
                - rendered_view
        """
        raise NotImplementedError()

    @classmethod
    def asinfodict(cls):
        return dict(gradeeditorid = cls.gradeeditorid,
                    title = cls.title,
                    description = cls.description,
                    config_editor_url = cls.config_editor_url,
                    draft_editor_url = cls.draft_editor_url)


class JsonRegistryItem(RegistryItem):
    """ RegistryItem with extra utility functions for use with JSON config and draft strings """
    @classmethod
    def decode_configstring(cls, configstring):
        """ Decode ``configstring`` using ``json.loads`` and return the result.
        Raise ConfigValidationError if it fails. """
        try:
            return json.loads(configstring)
        except ValueError, e:
            raise ConfigValidationError('Could not decode config string as JSON.')

    @classmethod
    def decode_draftstring(cls, draftstring):
        """ Decode ``draftstring`` using ``json.loads`` and return the result.
        Raise DraftValidationError if it fails. """
        try:
            return json.loads(draftstring)
        except ValueError, e:
            raise DraftValidationError('Could not decode config string as JSON.')

    @classmethod
    def validate_gradeeditor_key(cls, draftdct, expectedid):
        if not 'gradeeditor' in draftdct:
            raise DraftValidationError('The draftdct must contain the "gradeeditor" key.')
        gradeeditor = draftdct['gradeeditor']
        if not 'id' in gradeeditor or not 'version' in gradeeditor:
            raise DraftValidationError('The gradeeditor key must contain an object with id and version as keys.')
        if gradeeditor['id'] != expectedid:
            raise DraftValidationError('The gradeeditor id must be "{0}"'.format(expectedid))
        return gradeeditor

    @classmethod
    def validate_dict(cls, valuedict, exceptioncls, typedict):
        """
        Validate that each key in ``typedict`` is in ``valuedict``, and that
        the type of the values in ``valuedict`` reflects the types in
        ``typedict``.

        Raise ``exceptioncls`` with an error message if any validation fails.
        """
        if not isinstance(valuedict, dict):
            raise DraftValidationError('The draft string must contain a json map/object/dict.')
        for key, typecls in typedict.iteritems():
            if not key in valuedict:
                raise exceptioncls('{0} is required.'.format(key))
            if not isinstance(valuedict[key], typecls):
                raise exceptioncls('{0} must be of type: {1}.'.format(key, str(typecls)[7:-2]))




class Registry(object):
    """
    Grade editor registry. You **should not** create a object of this class.
    It is already available as :attr:`gradeeditor_registry`.
    """
    def __init__(self):
        self._registry = {}

    def register(self, registryitem):
        """
        Add a :class:`RegistryItem` to the registry.
        """
        if registryitem.gradeeditorid in self._registry:
            raise ValueError('More than one gradeeditor with gradeeditorid: {0}'.format(registryitem.gradeeditorid))
        self._registry[registryitem.gradeeditorid] = registryitem

    def __getitem__(self, gradeeditorid):
        return self._registry[gradeeditorid]

    def getdefaultkey(self):
        """
        Get the default key (the key defined in the DEVILRY_DEFAULT_GRADEEDITOR setting).
        """
        return settings.DEVILRY_DEFAULT_GRADEEDITOR

    def itertitles(self):
        """ Iterate over the registry yielding (key, title). """
        for key, item in self._registry.iteritems():
            yield key, item.title

    def iterinfordicts(self):
        for item in self._registry.itervalues():
            yield item.asinfodict()


gradeeditor_registry = Registry()
