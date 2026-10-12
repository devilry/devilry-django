from cradmin_legacy.renderable import AbstractRenderableWithCss


class AbstractItemRenderer(AbstractRenderableWithCss):
    """
    Abstract base class for :class:`.ItemFrameRenderer`
    and :class:`.ItemValueRenderer`.

    You will normally add objects of a class that extends this class
    to :class:`.List`, but it is not required.
    """

    #: If this is specified, we will add an attribute with this name
    #: for the value as an attribute of the object.
    #:
    #: I.e.: if ``valuealias = "person"``, you will be able to use ``me.person`` in
    #: the template, and you will be able to use ``self.person`` in any methods you
    #: add or override in the class (just remember to call ``super()`` if you override
    #: ``__init__``).
    valuealias = None

    def __init__(self, value, **kwargs):
        """
        Parameters:
            value: The value to render.
        """
        self.value = value
        self.kwargs = kwargs
        if self.valuealias:
            setattr(self, self.valuealias, self.value)


class ItemValueRenderer(AbstractItemRenderer):
    """
    The value renderer renders the value of each item in
    the :class:`.List`.
    """

    template_name = "cradmin_legacy/viewhelpers/listbuilder/base/itemvalue.django.html"

    def get_base_css_classes_list(self):
        """
        Override this to set your own css classes.
        """
        return ["cradmin-legacy-listbuilder-itemvalue"]


class ItemFrameRenderer(AbstractItemRenderer):
    """
    The outer item renderer provides a frame around the item.

    This is typically subclassed to:

    - Add visually highlighted frames for some items.
    - Add checkbox for each item
    - Make the item clickable (via an ``a`` tag or javascript).

    .. note::

        The :class:`.List` dors not require a :class:`.ItemFrameRenderer`,
        so lightweight lists without this extra wrapper is possible.

    .. attribute:: inneritem

        The renderable this frame wraps - an object of
        :class:`.ItemValueRenderer` or a subclass.
    """

    template_name = "cradmin_legacy/viewhelpers/listbuilder/base/itemframe.django.html"

    def __init__(self, inneritem, **kwargs):
        super().__init__(inneritem.value, **kwargs)
        self.inneritem = inneritem

    def get_base_css_classes_list(self):
        """
        Override this to set your own css classes.
        """
        return ["cradmin-legacy-listbuilder-itemframe"]


class List(AbstractRenderableWithCss):
    """
    A builder for HTML lists (can be used for other lists as well).

    Each item in the list is a :class:`.AbstractItemRenderer` object, and
    it is typically:

    - A subclass of :class:`.ItemValueRenderer` for simple lists.
    - A subclass of :class:`.ItemFrameRenderer` for more complex lists.

    .. note:: Items can be any :class:`cradmin_legacy.renderable.AbstractRenderableWithCss`, but that does not
        work with the shortcut methods:

        - :meth:`.extend_with_values`
        - :meth:`.from_value_iterable`
    """

    template_name = "cradmin_legacy/viewhelpers/listbuilder/base/list.django.html"

    def __init__(self):
        self.renderable_list = []

    def iter_renderables(self):
        """
        Get an iterator over the items in the list.
        """
        return iter(self.renderable_list)

    def has_items(self):
        """
        Returns:
            bool: ``True`` if the list has any items, and ``False`` otherwise.
        """
        return len(self.renderable_list) > 0

    def get_base_css_classes_list(self):
        """
        Sets ``cradmin-legacy-listbuilder-list`` as css class for the list.
        """
        return ["cradmin-legacy-listbuilder-list"]

    def append(self, renderable):
        """
        Appends an item to the list.

        Parameters:
            renderable: Must implement the :class:`cradmin_legacy.renderable.AbstractRenderableWithCss` interface,
                and it is typically a subclass of :class:`.AbstractItemRenderer`.
        """
        self.renderable_list.append(renderable)

    def extend(self, renerable_iterable):
        """
        Just like :meth:`.append` except that it takes an iterable
        of renderables instead of a single renderable.
        """
        self.renderable_list.extend(renerable_iterable)

    def get_default_value_renderer_class(self):
        """
        The default ``value_renderer_class`` for :meth:`.extend_with_values`.
        """
        return ItemValueRenderer

    def get_default_frame_renderer_class(self):
        """
        The default ``frame_renderer_class`` for :meth:`.extend_with_values`.
        """
        return None

    def extend_with_values(
        self, value_iterable, value_renderer_class=None, frame_renderer_class=None, value_and_frame_renderer_kwargs=None
    ):
        """
        Extends the list with an iterable of values.

        Parameters:
            value_iterable: An iterable of values to add to the list.
            value_renderer_class: A subclass of :class:`.ItemValueRenderer`.
                Defaults to :meth:`.get_default_value_renderer_class`.
            frame_renderer_class: A subclass of :class:`.ItemFrameRenderer`.

                If this is ``None``, the object added to the list will be an object of the
                ``value_renderer_class``.

                If this is specified, the object added to the list will be an object
                of the ``frame_renderer_class`` with an object of the ``value_renderer_class``
                as the ``inneritem`` attribute/parameter.

                Defaults to :meth:`.get_default_frame_renderer_class`.
            value_and_frame_renderer_kwargs (dict or function): Keyword arguments to send to all
                the constructor of all the value and frame renderers.

                If this is not a dict, it is assumed to be a function/callable that takes
                a value from the ``value_iterable`` as the only argument, and returns
                a dict of kwargs. Example function::

                    def my_kwargs_generator(value):
                        if value == 10:
                            return {
                                'is_selected': True
                            }
                        else:
                            return {}

                The ``value``-argument is sent as a positional argument, so your
                function can name the input argument as you like (so if the value
                is a ``Product`` object, you can use ``def my_kwargs_generator(product): ...``.
        """
        value_renderer_class = value_renderer_class or self.get_default_value_renderer_class()
        frame_renderer_class = frame_renderer_class or self.get_default_frame_renderer_class()
        value_and_frame_renderer_kwargs = value_and_frame_renderer_kwargs or {}
        for value in value_iterable:
            if isinstance(value_and_frame_renderer_kwargs, dict):
                kwargs = value_and_frame_renderer_kwargs
            else:
                kwargs = value_and_frame_renderer_kwargs(value)
            value_renderable = value_renderer_class(value=value, **kwargs)
            if frame_renderer_class:
                renderable = frame_renderer_class(inneritem=value_renderable, **kwargs)
            else:
                renderable = value_renderable
            self.append(renderable)

    @classmethod
    def from_value_iterable(
        cls,
        value_iterable,
        value_renderer_class=None,
        frame_renderer_class=None,
        value_and_frame_renderer_kwargs=None,
        **listkwargs,
    ):
        """
        A shortcut for creating an object of this class with the given ``**listkwargs``
        as __init__ arguments, and then calling :meth:`.extend_with_values` with
        ``value_iterable``, ``value_renderer_class`` and ``frame_renderer_class`` as
        arguments.

        See :meth:`.extend_with_values` for documentation for the arguments.

        Returns:
            An object of this class.
        """
        listobject = cls(**listkwargs)
        listobject.extend_with_values(
            value_iterable=value_iterable,
            value_renderer_class=value_renderer_class,
            frame_renderer_class=frame_renderer_class,
            value_and_frame_renderer_kwargs=value_and_frame_renderer_kwargs,
        )
        return listobject
