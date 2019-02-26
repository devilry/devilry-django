class GradingSystemPluginInterface(object):
    """
    Interface for new grading system plugins. Makes the grading system plugin
    ready for the global registry.

    This interface must be implemented by each grade plugin in the running system.
    this holds all the global information necessary to be able to
    manage the grade plugin layout and to cover smooth transition between different
    grade plugins on different Assignments

    """

    #: The ID of the registry. Should be a unique string, typically the python path of
    #: the module implementing the plugin.
    #: This attribute MUST be overidden by each plugin.
    id = None

    #: The title of the plugin. Should be a short title, and it should be translated.
    title = None

    #: The description of the plugin. Should be translated. Shown with css ``white-space:pre-wrap``.
    description = None

    #: ``True`` if the plugin require configuration before it can be used.
    #: If a plugin sets this to ``True``, :meth:`is_configured_correctly`
    #: and :meth:`.get_configuration_url` must be overridden.
    requires_configuration = False

    #: ``True`` if the plugin sets :attr:`devilry.apps.core.models.Assignment.passing_grade_min_points`
    #: automatically. If this is ``True``, the plugin must implement
    #: :meth:`.get_passing_grade_min_points`.
    sets_passing_grade_min_points_automatically = False

    #: ``True`` if the plugin sets :attr:`devilry.apps.core.models.Assignment.max_points`
    #: automatically. If this is ``True``, the plugin must implement
    #: :meth:`.get_max_points`.
    sets_max_points_automatically = False

    def __init__(self, assignment):
        self.assignment = assignment

    def get_passing_grade_min_points(self):
        """
        Get the value for :attr:`devilry.apps.core.models.Assignment.passing_grade_min_points`
        for this assignment.

        MUST be implemented when :obj:`.sets_passing_grade_min_points_automatically` is ``True``.
        """
        raise NotImplementedError("get_passing_grade_min_points() MUST be implemented when sets_passing_grade_min_points_automatically is True")

    def get_max_points(self):
        """
        Get the value for :attr:`devilry.apps.core.models.Assignment.max_points`
        for this assignment.

        MUST be implemented when :obj:`.sets_max_points_automatically` is ``True``.
        """
        raise NotImplementedError("get_max_points() MUST be implemented when sets_max_points_automatically is True")

    def is_configured(self):
        """
        Is the plugins configured in a manner that makes it ready for use on
        this assignment.

        MUST be implemented if :obj:`.requires_configuration` is ``True``.
        """
        raise NotImplementedError('is_configured() MUST be implemented when requires_configuration is True')

    def get_configuration_url(self):
        """
        Get the configuration URL for this plugin for this assignment.

        MUST be implemented if :obj:`.requires_configuration` is ``True``.
        """
        raise NotImplementedError('get_configuration_url() MUST be implemented when requires_configuration is True')


    def get_edit_feedback_url(self, deliveryid):
        """
        Get the feedback editing URL for this plugin for the given ``deliveryid``.

        :param deliveryid: The ID of the delivery to provide feedback for.
        """
        raise NotImplementedError("get_edit_feedback_url() MUST be implemented")

    def get_bulkedit_feedback_url(self, assignmentid):
        """
        Get the feedback editing URL for this plugin for the given ``assignmentid``.

        :param assignmentid: The ID of the delivery to provide feedback for.
        """
        raise NotImplementedError("get_bulkedit_feedback_url() MUST be implemented")

class GradingSystemPluginNotInRegistryError(Exception):
    """
    Raised by :meth:`.GradingSystemPluginRegistry.get` when a
    plugin that is not in the registry is requested.
    """


class NotGradingSystemPluginError(Exception):
    """
    Raised by :meth:`.GradingSystemPluginRegistry.add` when adding
    a plugin that is not a subclass of :class:`.GradingSystemPluginInterface`.
    """


class GradingSystemPluginRegistry(object):
    """
    Global Registry for grading system plugins.

    This registry holds information on each grading system plugin the current setup uses.

    The registry is used to decouple providing points for grades from the rest of the grading framework.
    """
    def __init__(self):
        self.items = {}

    def add(self, registryitemcls):
        """
        Add a plugin to the registry.

        :param registryitemcls:
            A subclass of :class:`.GradingSystemPluginInterface`.

        :raise NotGradingSystemPluginError:
            If ``registryitemcls`` is not a subclass of :class:`.GradingSystemPluginInterface`.
        """
        if not issubclass(registryitemcls, GradingSystemPluginInterface):
            raise NotGradingSystemPluginError('Items added to GradingSystemPluginRegistry must be subclasses of GradingSystemPluginInterface.')
        self.items[registryitemcls.id] = registryitemcls

    def __contains__(self, id):
        """
        Check if a plugin with the the given ``id`` is in the registry.
        """
        return id in self.items

    def __len__(self):
        """
        Get the number of plugins in the registry.
        """
        return len(self.items)

    def get(self, id):
        """
        Get a grading plugin API class by its ID.

        :raise GradingSystemPluginNotInRegistryError:
            If the plugin is not found in the registry.
        """
        try:
            return self.items[id]
        except KeyError:
            raise GradingSystemPluginNotInRegistryError('Grading system plugin with ID={} is not in the registry.'.format(id))

    def iter_with_assignment(self, assignment):
        """
        Returns an iterator over instances of all the plugins in the registry.
        Each instance is constructed with the given ``assignment`` as their
        first and only argument.
        """
        for item in self.items.values():
            yield item(assignment)


#: The grading system plugin registry. An instance of :class:`GradingSystemPluginRegistry`.
#: Plugins register themselves through this instance.
gradingsystempluginregistry = GradingSystemPluginRegistry()
