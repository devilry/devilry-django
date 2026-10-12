from django.forms.utils import flatatt
from django.template import defaultfilters

from django_cradmin import renderable


class BreadcrumbItem(renderable.AbstractBemRenderable):
    """
    Breadcrumb item renderable.
    """

    template_name = "django_cradmin/crbreadcrumb/breadcrumb-item.django.html"

    def __init__(
        self,
        label,
        url=None,
        active=False,
        label_maxlength=None,
        active_label_maxlength=None,
        render_link_for_active=False,
        parent_bem_block=None,
    ):
        """

        Args:
            label (str): The text/label.
            url (str): The link URL. If this is `None` or any other boolean false value,
                we render the item as a `<span>` instead of as a `<a>` element.
            active (bool): If this is ``True``, we add the ``--active`` BEM variant to the element.
            label_maxlength (int): The max length of the label before it is shortened using the
                ``truncatechars`` django template filter.
                You typically do not set this directly, but instead override
                :meth:`.BreadcrumbItemList.get_default_item_label_maxlength` to get
                uniformed max lengths for all your breadcrumbs.
            active_label_maxlength (int): The max length of the label if active=True before the label
                is shortened using the ``truncatechars`` django template filter.
                You typically do not set this directly, but instead override
                :meth:`.BreadcrumbItemList.get_default_active_item_label_maxlength` to get
                uniformed max lengths for all your breadcrumbs.
            render_link_for_active (bool): If this is ``True``, we render as a link (``<a>``)
                even if ``active`` is ``True``. We do, of course, not render
                as a link if we do not have an ``url``.
            parent_bem_block: Provided automatically by :class:`.BreadcrumbItemList`.
        """
        self.url = url
        self.label = label
        self.active = active
        self.label_maxlength = label_maxlength
        self.active_label_maxlength = active_label_maxlength
        self.render_link_for_active = render_link_for_active
        self.parent_bem_block = parent_bem_block
        super(BreadcrumbItem, self).__init__()

    def get_bem_element(self):
        return "{}__item".format(self.parent_bem_block)

    def get_bem_variant_list(self):
        variant_list = []
        if self.active:
            variant_list.append("active")
        return variant_list

    def should_render_as_link(self):
        """
        Should we render the element as a link (``<a>``)?
        """
        if self.active and not self.render_link_for_active:
            return False
        return bool(self.url)

    @property
    def html_tag(self):
        if self.should_render_as_link():
            return "a"
        return "span"

    @property
    def truncated_label(self):
        if self.active:
            label_maxlength = self.active_label_maxlength
        else:
            label_maxlength = self.label_maxlength

        if label_maxlength:
            return defaultfilters.truncatechars(self.label, label_maxlength)
        return self.label

    def get_html_element_attributes(self):
        """
        Get HTML element attributes as a dict.
        """
        html_element_attributes = {
            "class": self.css_classes or False,  # Fall back to false to avoid class=""
        }
        if self.should_render_as_link():
            html_element_attributes["href"] = self.url
        return html_element_attributes

    @property
    def html_element_attributes_string(self):
        return flatatt(self.get_html_element_attributes())


class BreadcrumbSeparator(renderable.AbstractBemRenderable):
    """
    Breadcrumb separator renderable.
    """

    template_name = "django_cradmin/crbreadcrumb/breadcrumb-separator.django.html"

    def __init__(self, parent_bem_block=None):
        self.parent_bem_block = parent_bem_block
        super(BreadcrumbSeparator, self).__init__()

    def get_bem_element(self):
        return "{}__separator".format(self.parent_bem_block)


class BreadcrumbItemList(renderable.AbstractBemRenderable):
    """
    List of breadcrumb items.

    We provide a lot of helper methods, but if you need more powerful features, such
    as removal of breadcrumb items, you can just manipulate the
    :attr:`~.BreadcrumbItemList.breadcrumb_item_list` attribute directly. All the append*, insert*, etc.
    methods just add items to this list.

    Attributes:
        breadcrumb_item_list (list): A plain python list of
            :class:`django_cradmin.renderable.AbstractRenderable` objects,
            normally :class:`.BreadcrumbItem` objects.
        cradmin_instance (django_cradmin.crinstance.BaseCrAdminInstance): The
            cradmin instance sent in as an argument to ``__init__()``.
    """

    template_name = "django_cradmin/crbreadcrumb/breadcrumb-item-list.django.html"

    #: Render location: Above page cover.
    LOCATION_ABOVE_PAGE_COVER = "above-page-cover"

    #: Render location: Below page cover.
    LOCATION_BELOW_PAGE_COVER = "below-page-cover"

    @classmethod
    def from_breadcrumb_item_list(cls, breadcrumb_item_list, **kwargs):
        new_breadcrumb_item_list = cls(cradmin_instance=breadcrumb_item_list.cradmin_instance, **kwargs)
        new_breadcrumb_item_list.extend_with_item_renderables(breadcrumb_item_list.breadcrumb_item_list)
        return new_breadcrumb_item_list

    def __init__(self, cradmin_instance):
        """

        Args:
            cradmin_instance (django_cradmin.crinstance.BaseCrAdminInstance): A cradmin instance.
        """
        self.breadcrumb_item_list = []
        self.cradmin_instance = cradmin_instance
        self._overridden_location = None
        super(BreadcrumbItemList, self).__init__()

    def get_extra_css_classes_list(self):
        return ["hidden-in-print"]

    def get_default_location(self):
        """
        The location to render the breadcrumb at by default.

        Can be overridden on a per view, per app or per cradmin instance
        basis using :meth:`.set_location`.

        Only relevant if using the
        :func:`django_cradmin.templatetags.cradmin_tags.cradmin_render_breadcrumb_item_list`
        template tag with the ``location`` argument.
        Defaults to :obj:`~.BreadcrumbItemList.LOCATION_BELOW_PAGE_COVER`.
        """
        return self.LOCATION_BELOW_PAGE_COVER

    def get_location(self):
        """
        Get the location to render the breadcrumb item list at.

        Do not override this - override :meth:`.get_default_location`
        instead.
        """
        return self._overridden_location or self.get_default_location()

    def set_location(self, location):
        """
        Set the location to render the breadcrumb item list at.

        Can be used in the ``get_breadcrumb_item_list_renderable()``
        method of cradmin instances, apps or views to override the
        location to render breadcrumbs at.

        Args:
            location (str): Location.
        """
        self._overridden_location = location

    def should_render_at_location(self, location):
        return location is None or location == self.get_location()

    def get_bem_block(self):
        """
        Override this to use a custom BEM block for the breadcrumb.
        """
        return "breadcrumb-item-list"

    def get_bem_variant_list(self):
        return ["location-{}".format(self.get_location())]

    def __len__(self):
        return len(self.breadcrumb_item_list)

    def __bool__(self):
        return len(self) > 0

    def get_separator_renderable_class(self):
        """
        Get the renderable class for breadcrumb item separators.

        Defaults to :class:`.BreadcrumbSeparator`.
        """
        return BreadcrumbSeparator

    def make_separator_renderable(self):
        """
        Make a breadcrumb item separator renderable.
        """
        return self.get_separator_renderable_class()(parent_bem_block=self.get_bem_block())

    def get_item_renderable_class(self):
        """
        Get the renderable class for breadcrumb items.

        Defaults to :class:`.BreadcrumbItem`.
        """
        return BreadcrumbItem

    def get_default_item_label_maxlength(self):
        """
        The default max length of the label of items.

        If the label is longer than this, the label is truncated
        using the ``truncatechars`` django template filter.

        If you return None or another boolean false falue from this method,
        labels are not truncated.

        Returns:
            int: The max length of item labels, or ``None``. Defaults to ``15``.
        """
        return 15

    def get_default_active_item_label_maxlength(self):
        """
        The default max length of the label of active items.

        If the label is longer than this, the label is truncated
        using the ``truncatechars`` django template filter.

        If you return None or another boolean false falue from this method,
        labels are not truncated.

        Returns:
            int: The max length of item labels, or ``None``. Defaults to ``25``.
        """
        return 25

    def get_item_renderable_kwargs(self, **extra_kwargs):
        """
        Get kwargs for the :meth:`.get_item_renderable_class`.

        Make sure you call super to get the required kwargs if you
        override this method.

        Args:
            **extra_kwargs: Extra kwargs.

        Returns:
            dict: kwargs.
        """
        kwargs = {
            "parent_bem_block": self.get_bem_block(),
            "label_maxlength": self.get_default_item_label_maxlength(),
            "active_label_maxlength": self.get_default_active_item_label_maxlength(),
        }
        kwargs.update(extra_kwargs)
        return kwargs

    def make_item_renderable(self, **kwargs):
        """
        Make an item renderable.

        Args:
            **kwargs: Kwargs for the item renderable class. This is forwarded to
                :meth:`.get_item_renderable_kwargs` to enable default kwargs for all
                items in the breadcrumb item list.
        """
        return self.get_item_renderable_class()(**self.get_item_renderable_kwargs(**kwargs))

    def append(self, **kwargs):
        """
        Uses :meth:`.make_item_renderable` to create a renderable,
        and appends the created item to the breadcrumb list.
        """
        self.append_item_renderable(self.make_item_renderable(**kwargs))

    def prepend(self, **kwargs):
        """
        Uses :meth:`.make_item_renderable` to create a renderable,
        and prepends the created item to the breadcrumb list.
        """
        self.prepend_item_renderable(self.make_item_renderable(**kwargs))

    def insert(self, index, **kwargs):
        """
        Uses :meth:`.make_item_renderable` to create a renderable,
        and inserts the created item in the breadcrumb list.
        """
        self.insert_item_renderable(index, self.make_item_renderable(**kwargs))

    def clear(self):
        self.breadcrumb_item_list.clear()

    def remove_last(self):
        if len(self.breadcrumb_item_list) > 0:
            self.breadcrumb_item_list.pop()

    def remove_first(self):
        if len(self.breadcrumb_item_list) > 0:
            del self.breadcrumb_item_list[0]

    def insert_item_renderable(self, index, renderable_object):
        """
        Insert a renderable object at a specific index in the breadcrumb list.

        Args:
            index (int): The index to insert at.
            renderable_object: The renderable object (a subclass
                of :class:`django_cradmin.renderable.AbstractRenderable`)
        """
        if index < len(self.breadcrumb_item_list):
            self.breadcrumb_item_list.insert(index, renderable_object)
        else:
            self.append_item_renderable(renderable_object)

    def prepend_item_renderable(self, renderable_object):
        """
        Prepend a renderable object to the breadcrumb list.

        Args:
            renderable_object: The renderable object (a subclass
                of :class:`django_cradmin.renderable.AbstractRenderable`)
        """
        self.breadcrumb_item_list.insert(0, renderable_object)

    def append_item_renderable(self, renderable_object):
        """
        Append a renderable object to the breadcrumb list.

        Args:
            renderable_object: The renderable object (a subclass
                of :class:`django_cradmin.renderable.AbstractRenderable`)
        """
        self.breadcrumb_item_list.append(renderable_object)

    def extend_with_item_renderables(self, renerable_iterable):
        """
        Just like :meth:`.append` except that it takes an iterable
        of renderables instead of a single renderable.
        """
        self.breadcrumb_item_list.extend(renerable_iterable)

    def iter_breadcrumb_list_renderables(self):
        """
        Iterate through all the breadcrumb items and separators.

        Separators is yielded automatically after each item except the last
        one. Separator renderables can be overridden with
        :meth:`.make_separator_renderable`.
        """
        for index, breadcrumb_item in enumerate(self.breadcrumb_item_list):
            yield breadcrumb_item
            if index < len(self.breadcrumb_item_list) - 1:
                yield self.make_separator_renderable()


class BreadcrumbItemListWrapper(renderable.AbstractBemRenderable):
    """
    Wraps a :class:`.BreadcrumbItemList` in a box.
    """

    template_name = "django_cradmin/crbreadcrumb/breadcrumb-item-list-wrapper.django.html"

    def __init__(self, breadcrumb_item_list):
        self.breadcrumb_item_list = breadcrumb_item_list
        super(BreadcrumbItemListWrapper, self).__init__()

    def get_bem_block(self):
        return "breadcrumb-item-list-wrapper"

    def get_bem_variant_list(self):
        return ["location-{}".format(self.breadcrumb_item_list.get_location())]

    def get_breadcrumb_item_list_extra_context_data(self):
        return {"is_within_wrapper": True}

    @property
    def container_css_classes(self):
        return "container container--wide"


class WrappedBreadcrumbItemList(BreadcrumbItemList):
    """
    Renders and works just like :class:`.BreadcrumbItemList` except that
    it is wrapped within a :class:`.BreadcrumbItemListWrapper`.

    You can subclass :class:`.BreadcrumbItemListWrapper` and replace the wrapper
    class by overriding :meth:`.get_wrapper_renderable_class`.
    """

    def get_wrapper_renderable_class(self):
        """
        Get the renderable for the wrapper element(s).

        Returns:
            django_cradmin.crbreadcrumb.BreadcrumbItemListWrapper: :class:`.BreadcrumbItemListWrapper`
            or a subclass.

        """
        return BreadcrumbItemListWrapper

    def get_wrapper_renderable_kwargs(self):
        """
        Get kwargs for the class returned by :meth:`.get_wrapper_renderable_class`.

        Returns:
            dict: Kwargs.
        """
        return {"breadcrumb_item_list": self}

    def make_wrapper_renderable(self):
        return self.get_wrapper_renderable_class()(**self.get_wrapper_renderable_kwargs())

    def render(self, request=None, extra_context_data=None):
        extra_context_data = extra_context_data or {}
        if extra_context_data.get("is_within_wrapper"):
            return super(WrappedBreadcrumbItemList, self).render(request=request, extra_context_data=extra_context_data)
        else:
            return self.make_wrapper_renderable().render(request=request, extra_context_data=extra_context_data)
