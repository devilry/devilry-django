"""
.. attribute:: registry

    A :class:`Registry`-object.
"""


from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType


class GradePluginError(Exception):
    """ Base class for grade plugin errors. """

class GradePluginDoesNotExistError(GradePluginError):
    """ Raised when a grade plugin does not exist. """

class WrongContentTypeError(GradePluginError):
    """ Raised when the grade object on a feedback is not using the grade
    plugin on the assignment. """


class XmlrpcGradeConf(object):
    """ Provides the configuration-wrapper between a grade-plugin and the
    xmlrpc. """
    def __init__(self, help=None, filename=None,
            default_filecontents_callback=None):
        """
        All parameters are stored as object attributes.

        :param help:
            Help text explaining the format of the grade.
        :param filename:
            The reccommended filename. ``None`` means that no file is
            required.  Note that this is only a hint to the xmlrpc, and
            might be ignored.
        :param default_filecontents_callback:
            A function which returns the reccommended default contents of
            the grade-file. The function takes a
            :class:`devilry.core.models.Assignment` object as it's only
            argument.
        """
        self.help = help
        self.filename = filename
        self.default_filecontents_callback = default_filecontents_callback

    def as_dict(self, assignmentobj):
        """
        Get a dict with all the attributes except
        ``default_filecontents_callback`` which instead is called with
        ``assignmentobj`` as argument, and the result is stored with the
        ``"default_filecontents"``-key.
        """
        if self.default_filecontents_callback:
            default_filecontents = self.default_filecontents_callback(
                    assignmentobj)
        else:
            default_filecontents = None
        return dict(help=self.help, filename=self.filename,
                default_filecontents=default_filecontents)


class GradeModel(models.Model):
    @classmethod
    def calc_final_grade(self, period, gradeplugin_key, user):
        return None

    def get_feedback_obj(self):
        from devilry.core.models import Feedback # must be imported here to avoid recursive include
        typ = ContentType.objects.get_for_model(self)
        return Feedback.objects.get(content_type=typ.id,
                object_id=self.id)

    def get_grade_as_short_string(self, feedback_obj):
        """ Return a string representation of the grade suitable for
        short one-line display. This method is required.
        
        :param feedback_obj:
            The :class:`devilry.core.models.Feedback` using this
            grade-object.
        """
        raise NotImplementedError()

    def get_grade_as_long_string(self, feedback_obj):
        """
        Return a string representation of the grade which might span
        multiple lines. The string must be formatted with restructured text.
        
        :param feedback_obj:
            The :class:`devilry.core.models.Feedback` using this
            grade-object.
        :return: None if this operation is not supported (the default).
        """
        return None

    def get_grade_as_xmlrpcstring(self, feedback_obj):
        """
        Get the grade from a string compatible with
        :meth:`set_grade_from_xmlrpcstring`. This is primarly intended for
        xmlrpc, and a grade-plugin is not required to support it. If
        unsupported, just do not override it, and it will default to raising
        :exc:`NotImplementedError`, which the core and xmlrpc handles.
        
        :param feedback_obj:
            The :class:`devilry.core.models.Feedback` using this
            grade-object.
        :return: None if this operation is not supported (the default).
        """
        raise None

    def set_grade_from_xmlrpcstring(self, grade, feedback_obj):
        """
        Set the grade from string. This is primarly intended for xmlrpc, and
        a grade-plugin is not required to support it. If unsupported, just
        do not override it, and it will default to raising
        :exc:`NotImplementedError`, which the core and xmlrpc handles.

        :param feedback_obj:
            The :class:`devilry.core.models.Feedback` using this
            grade-object.

        Raises :exc:`NotImplementedError` if the operation is not supported.
        """
        raise NotImplementedError()


class RegistryItem(object):
    """
    Information about a grade plugin.
    """
    def __init__(self, view, model_cls, label, description,
           admin_url_callback=None, xmlrpc_gradeconf=None):
        """   
        All parameters are stored as object attributes.

        :param view:
            The view used when creating feedback with this grade-plugin.
            See :ref:
        :param model_cls:
            A class for storing the grade of a single Feedback. It us used in a
            one-to-one relationship with :class:`devilry.core.models.Feedback`
            (The Feedback-class takes care of the relationship).
        """
        self.view = view
        self.xmlrpc_gradeconf = xmlrpc_gradeconf
        self.model_cls = model_cls
        self.label = label
        self.description = description
        self.admin_url_callback = admin_url_callback

    def get_key(self):
        meta = self.model_cls._meta
        return '%s:%s' % (meta.app_label, meta.module_name)

    def get_content_type(self):
        meta = self.model_cls._meta
        #print dir(meta)
        #for ct in ContentType.objects.all():
        #    print ct.model
        #print meta.app_label, meta.module_name
        return ContentType.objects.get(app_label=meta.app_label,
                model=meta.module_name)

    def __str__(self):
        return self.label


class Registry(object):
    """
    Grade-plugin registry. You do not need to create a object of this class.
    It is already available as :attr:`registry`.
    """
    def __init__(self):
        self._registry = {}

    def register(self, registryitem):
        """
        Add a :class:`RegistryItem` to the registry.
        """
        self._registry[registryitem.get_key()] = registryitem

    def getitem(self, key):
        """
        Get the :class:`RegistryItem` registered with the given ``key``.
        """
        return self._registry[key]

    def getdefaultkey(self):
        """
        Get the default key (the key defined in the
        DEVILRY_DEFAULT_GRADEPLUGIN setting).
        """
        return settings.DEVILRY_DEFAULT_GRADEPLUGIN

    def iterlabels(self):
        """ Iterate over the registry yielding (key, label). """
        values = self._registry.values()
        values.sort(key=lambda i: i.label)
        for v in values:
            yield (v.get_key(), v)

    def iteritems(self):
        """ Iterate over the registry yielding (key, RegistryItem). """
        return self._registry.iteritems()

    def __iter__(self):
        return self.iterlabels()


registry = Registry()
