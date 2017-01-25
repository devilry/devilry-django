# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# ievv_opensource imports
from ievv_opensource.utils.singleton import Singleton


class DuplicatePluginTypeError(Exception):
    """
    Exception raised when trying to add multiple :class:`.PageType`
    with the same :meth:`~.PageType.get_pagetypeid` to the :class:`.Registry`.
    """


class PluginType(object):
    """
    Defines a PluginType in the :class:`.Registry`
    """

    #: A unique ID for the PageType.
    #: The convention is to use ``<appname>.<plugintype classname>``, but as long as it is
    #: unique and only contains ``_``, ``a-z``, ``A-Z``, ``0-9`` and ``.``, it can be anything you like.
    #: Never read this directly - use :meth:`.get_plugintypeid`.
    plugintypeid = None

    #: A human readable name for plugin type.
    #: Should be set, but defaults to :obj:`~.PluginType.pagetypeid`
    human_readable_name = None

    #: A description of the plugin in plain text.
    #: Should describe what the plugin does.
    #: Should be set, but defuaults to 'Description not available'.
    description = 'Description not available'

    @classmethod
    def get_plugintypeid(cls):
        """
        Get :obj:`~.PageType.pagetypeid`.
        You can override this if you need to dynamically determine the
        ``plugintypeid``.
        """
        return cls.plugintypeid

    def __init__(self):
        if self.__class__.get_plugintypeid() is None:
            raise ValueError('plugintypeid is required')

    def get_human_readable_name(self):
        """
        Get :obj:`~.PluginType.human_readable_name`, falling back to
        :meth:`~.PluginType.get_plugintypeid` if it is not set.

        Returns:
            str: :obj:`~.PluginType.human_readable_name` or :obj:`~.PluginType.plugintypeid`.
        """
        return self.human_readable_name or self.__class__.get_plugintypeid()

    def get_plugin_view_class(self):
        """
        Get the view class the plugin should use.

        This is the first view the user is sent to when selecting the plugin.
        """
        raise NotImplementedError()

    def get_description(self):
        """
        Get the description that explains what the plugin is for.

        Returns:
            str: A description for the plugin.
        """
        return self.description


class Registry(Singleton):
    """
    Registry of `qualifies for exam` plugins as plugin types. Each PluginType is added as a :class:`.PluginType` object.
    """
    def __init__(self):
        super(Registry, self).__init__()
        self._plugintypeclasses = {}

    def __get_classpath(self):
        return '{}.{}'.format(self.__module__, self.__class__.__name__)

    def add(self, registryplugin):
        """
        Add a plugin to the registry.

        Args:
            registryplugin (:class:`.PageType`): plugin.
        """
        if registryplugin.plugintypeid in self._plugintypeclasses:
            raise DuplicatePluginTypeError('Duplicate plugintypeid in {}: {}'.format(
                    self.__get_classpath(),
                    registryplugin.plugintypeid
            ))
        self._plugintypeclasses[registryplugin.get_plugintypeid()] = registryplugin

    def __getitem__(self, plugintypeid):
        return self._plugintypeclasses[plugintypeid]

    def __iter__(self):
        return iter(self._plugintypeclasses.values())

    def __contains__(self, plugintypeid):
        return plugintypeid in self._plugintypeclasses

    def iterchoices(self):
        """
        Iterate over the :class:`plugintypes <.PluginType>` in the registry
        yielding where the value is the :obj:`.PluginType.plugintypeid`

        Returns:
            An iterator that yields ``<plugintypeid>`` for each :class:`.PluginType` in the registry.
            The iterator is sorted by :meth:`.PluginType.get_plugintypeid`.
        """
        for registryplugin in sorted(self._plugintypeclasses.values()):
            yield registryplugin.get_plugintypeid


class PluginTypeSubclassFactory(object):
    """
    Creates a instance of :class:`.PluginType` for use in tests.
    """
    @classmethod
    def make_subclass(cls,
                      classname,
                      plugintypeid,
                      human_readable_name=None,
                      description='Description not available',
                      plugin_view_class=None):
        """
        Creates a subclass of :class:`.PluginType` with required arguments.

        Args:
            classname: Name of the subclass.
            plugintypeid: Required plugintypeid.
            human_readable_name: (optional).
            description: What the plugin is for(optional).
            plugin_view_class: The view class for the plugin(optional).

        Returns:

        """

        def get_plugin_view_class(self):
            return plugin_view_class

        plugin_subclass = type(classname, (PluginType,), {
            'plugintypeid': plugintypeid,
            'human_readable_name': human_readable_name,
            'description': description,
            'get_plugin_view_class': get_plugin_view_class
        })
        return plugin_subclass


class MockableRegistry(Registry):
    """
    A non-singleton version of :class:`.Registry` for use in tests.
    """
    def __init__(self):
        self._instance = None  # Ensure the singleton-check is not triggered
        super(MockableRegistry, self).__init__()

    @classmethod
    def make_mockregistry(cls, *plugintype_classes):
        """
        Shortcut for making a mock registry.

        Args:
            *plugintype_classes: :class:`.PluginType` classes to add.


        Returns:
            An object of this class with the requested :class:`.PluginType` classes registered.
        """
        mockregistry = cls()
        for pagetype_class in plugintype_classes:
            mockregistry.add(pagetype_class)
        return mockregistry
