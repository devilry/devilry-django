"""
.. attribute:: gradeeditor_registry

    A :class:`Registry`-object.
"""
import json
from django.conf import settings
from django.core.exceptions import ValidationError


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
    """
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
    def draft_to_staticfeedback_kwargs(cls, draftstring):
        """
        Convert ``draftstring`` into a dictionary of keyword arguments for StaticFeedback.
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
    def validate_dict(cls, valuedict, exceptioncls, typedict):
        """
        Validate that each key in ``typedict`` is in ``valuedict``, and that
        the type of the values in ``valuedict`` reflects the types in
        ``typedict``.

        Raise ``exceptioncls`` with an error message if any validation fails.
        """
        for key, value in valuedict.iteritems():
            if not key in typedict:
                raise exceptioncls('{0} is required.'.format(key))
            if not isinstance(value, typedict[key]):
                raise exceptioncls('{0} must be of type: {1}.'.format(key, typedict[key]))




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
