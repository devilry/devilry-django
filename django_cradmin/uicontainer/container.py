from django.conf import settings
from django.forms.utils import flatatt
from django_cradmin import renderable


class NotBootsrappedError(Exception):
    """
    Raised when trying to use features of
    :class:`.AbstractContainerRenderable`
    that requires is to have been bootstrapped.
    """


class AlreadyBootsrappedError(Exception):
    """
    Raised when trying to :meth:`~.AbstractContainerRenderable.bootstrap`
    and already bootstrapped :class:`.AbstractContainerRenderable`.
    """


class NotAllowedToAddChildrenError(Exception):
    """
    Raised when trying to add children to a :class:`.AbstractContainerRenderable`
    where :meth:`~.AbstractContainerRenderable.html_tag_supports_children`
    returns ``False``.
    """


class UnsupportedHtmlTagError(ValueError):
    """
    Raised when providing an invalid ``html_tag`` kwarg to :class:`.AbstractContainerRenderable`.

    See :obj:`.AbstractContainerRenderable.supported_html_tags`.
    """


class InvalidBemError(ValueError):
    """
    Raised when invalid BEM is supplied.
    """


class InvalidDomIdError(ValueError):
    """
    Raised when invalid dom_id is supplied.
    """


class AbstractContainerRenderable(renderable.AbstractRenderableWithCss):
    """
    Base class for all renderables in the uicontainer framework.

    This can not be used directly. You extend it, and at least override
    :meth:`.get_default_html_tag`, or use one of the subclasses.

    The most basic subclass is :class:`django_cradmin.uicontainer.div.Div`.

    .. attribute:: parent

        The parent AbstractContainerRenderable. Set in :meth:`.bootstrap`.
        The attribute does not exist if :meth:`.bootstrap` has not been
        run. Is ``None`` if this is the root of the container tree.

    .. attribute:: properties

        A dict of properties. These properties is copied down to the
        ``properties`` attribute of children (with the update-method, not full replace)
        in :meth:`.bootstrap`.
        This means that you can add properties in ``__init__()``,
        and make them available to any children recursively.
    """

    template_name = "django_cradmin/uicontainer/container.django.html"

    #: You can override this to specify a set of supported HTML tags
    #: for the ``html_tag`` attribute for :meth:`~.AbstractContainerRenderable.__init__`.
    #: This is useful to avoid typing errors. It should not be a big problem if you
    #: forget a tag that should be supported - developers can just create a subclass.
    #:
    #: If the value of this field is None, or any other value that is considered False by
    #: ``bool()``, we do not validate the ``html_tag`` kwarg.
    supported_html_tags = None

    def __init__(
        self,
        children=None,
        bem_block=None,
        bem_element=None,
        bem_variant_list=None,
        html_tag=None,
        css_classes_list=None,
        extra_css_classes_list=None,
        test_css_class_suffixes_list=None,
        role=False,
        dom_id=False,
        html_element_attributes=None,
        **kwargs,
    ):
        """
        Args:
            children: List of children. Children must be objects of subclasses
                of :class:`.AbstractContainerRenderable`.
            css_classes_list (list): Override the :meth:`default css classes <.get_default_css_classes_list>`
                with your own list of css classes.
            extra_css_classes_list (list): Add extra css classes. This is appended to
                the css classes in the ``css_classes_list`` kwarg if that is specified,
                or appended to the css classes returned by
                :meth:`.get_default_css_classes_list`.
            role (str): The value of the role attribute.
                If this is not specified, we fall back on the value returned
                by :meth:`.get_default_role`.
                If both is ``False``, we do not render the role attribute.
            dom_id (str): The value of the id attribute.
                If this is not specified, we fall back on the value returned
                by :meth:`.get_default_dom_id`.
                If both is ``False``, we do not render the id attribute.
            html_element_attributes (dict): HTML element attributes to add
                to the HTML element. This adds attributes returned
                by :meth:`.get_html_element_attributes`. If this dict includes
                attributes returned by :meth:`.get_html_element_attributes`,
                the attributes specified in this kwarg takes presedense.
                The format of the dict is specified in :meth:`.get_html_element_attributes`.
        """
        self.kwargs = kwargs
        self.validate_dom_id(dom_id=dom_id)
        self.validate_bem(bem_block=bem_block, bem_element=bem_element)
        self.validate_html_tag(html_tag=html_tag)
        self._childrenlist = []
        self._virtual_childrenlist = []
        self._is_bootstrapped = False
        self.properties = {}
        self._overridden_bem_block_or_element = bem_block or bem_element
        self._overridden_bem_variant_list = bem_variant_list
        self._overridden_role = role
        self._overridden_dom_id = dom_id
        self._overridden_html_tag = html_tag
        self._html_element_attributes = html_element_attributes
        self._overridden_css_classes_list = css_classes_list
        self._overridden_test_css_class_suffixes_list = test_css_class_suffixes_list
        self._extra_css_classes_list = extra_css_classes_list
        self.add_children(*self.prepopulate_children_list())
        self.add_virtual_children(*self.prepopulate_virtual_children_list())
        if children:
            self.add_children(*children)

    def should_validate_dom_id(self):
        """
        Should we raise :class:`.InvalidDomIdError` exception
        when the ``dom_id`` kwarg is malformed.

        Returns the value of the :setting:`DJANGO_CRADMIN_UICONTAINER_VALIDATE_DOM_ID`
        setting, falling back to ``True`` if it is not defined.

        The validator requires the dom_id
        to start with ``id_``, be lowercase, and not contain ``-``.

        We recommend to not override this to ensure uniform DOM id naming.

        You should disable this validation in production using the
        :setting:`DJANGO_CRADMIN_UICONTAINER_VALIDATE_DOM_ID` setting.
        """
        return getattr(settings, "DJANGO_CRADMIN_UICONTAINER_VALIDATE_DOM_ID", True)

    def should_validate_bem(self):
        """
        Should we raise :class:`.InvalidBemIdError` exception
        when the ``bem_block`` or ``bem_element`` kwarg is malformed?

        Returns the value of the :setting:`DJANGO_CRADMIN_UICONTAINER_VALIDATE_BEM`
        setting, falling back to ``True`` if it is not defined.

        The validator requires the bem_block to not contain ``__``
        (double underscore), and the bem_element to comtain ``__`` (double
        underscore).

        We recommend to not chanding this to ensure BEM elements and
        blocks are used correctly.

        You should disable this validation in production using the
        :setting:`DJANGO_CRADMIN_UICONTAINER_VALIDATE_BEM` setting.
        """
        return getattr(settings, "DJANGO_CRADMIN_UICONTAINER_VALIDATE_BEM", True)

    def validate_dom_id(self, dom_id):
        if dom_id is False:
            return
        if not self.should_validate_dom_id():
            return
        normalized_dom_id = dom_id.replace("-", "").lower()
        if not dom_id.startswith("id_") or dom_id != normalized_dom_id:
            raise InvalidDomIdError(
                'dom_id must begin with "id_", be all lowercase, and can not contain "-". '
                "{dom_id!r} does not match this requirement.".format(dom_id=dom_id)
            )

    def validate_bem(self, bem_block, bem_element):
        if not self.should_validate_bem():
            return
        if bem_block and bem_element:
            raise InvalidBemError(
                "Can not specify both bem_element or bem_block. An "
                "HTML element is eighter a BEM block or a BEM element."
            )
        if bem_block:
            if "__" in bem_block:
                raise InvalidBemError(
                    "{bem_block} is not a valid BEM block name. "
                    'BEM blocks do not contain "__". Are you sure you '
                    "did not mean to use the bem_element kwarg?".format(bem_block=bem_block)
                )
        elif bem_element:
            if "__" not in bem_element:
                raise InvalidBemError(
                    "{bem_element} is not a valid BEM element name. "
                    'BEM elements must contain "__". Are you sure you '
                    "did not mean to use the bem_block kwarg?".format(bem_element=bem_element)
                )

    def get_full_class_path_as_string(self):
        """
        Get full class path as string.

        Useful for providing some extra information in exceptions.
        Normally this will be in a traceback, but when dealing with
        things rendered by a Django template, this information is not
        always included.
        """
        return "{}.{}".format(self.__class__.__module__, self.__class__.__name__)

    def validate_html_tag(self, html_tag):
        if html_tag and self.supported_html_tags and html_tag not in self.supported_html_tags:
            raise UnsupportedHtmlTagError(
                "Unsupported HTML tag for {classpath}: {html_tag}".format(
                    classpath=self.get_full_class_path_as_string(), html_tag=self._overridden_html_tag
                )
            )

    def get_default_html_tag(self):
        """
        Get the default HTML tag to wrap renderable in.

        Can be overriden by the ``html_tag`` kwarg for :meth:`.__init__`.

        Returns ``"div"`` by default.
        """
        return "div"

    @property
    def html_tag(self):
        """
        Get the HTML tag for this container.
        """
        return self._overridden_html_tag or self.get_default_html_tag()

    @property
    def html_tag_supports_children(self):
        """
        Does the html tag support children?

        If this returns ``False``, we:

        - Do not render an end tag for the wrapper element.
        - Do not allow children to be added to the container.

        Should be overridden to return ``False`` if the :meth:`.get_default_html_tag`
        does not allow for children. Examples of this case is if the
        wrapper html tag i ``input`` or ``hr``.

        See also :meth:`.can_have_children`, which should be used if the HTML tag
        should have and end tag, but not children.

        Returns:
            boolean: True by default.
        """
        return True

    @property
    def can_have_children(self):
        """
        Can this container have children?

        If this returns ``False``, :meth:`.add_child` will raise
        :class:`.NotAllowedToAddChildrenError`.

        Returns:
            boolean: The return value from :meth:`.html_tag_supports_children` by default.
        """
        return self.html_tag_supports_children

    def get_default_role(self):
        """
        Get the default value for the role attribute of the html element.

        Defaults to ``False``.
        """
        return False

    @property
    def role(self):
        """
        Get the value for the role attribute of the html element.

        You should not override this. Override :meth:`.get_default_role` instead.
        """
        return self._overridden_role or self.get_default_role()

    def get_default_dom_id(self):
        """
        Get the default value for the id attribute of the html element.

        Defaults to ``False``.
        """
        return False

    @property
    def dom_id(self):
        """
        Get the value for the id attribute of the html element.

        You should not override this. Override :meth:`.get_default_dom_id` instead.
        """
        return self._overridden_dom_id or self.get_default_dom_id()

    def get_html_element_attributes(self):
        """
        Get HTML element attributes as a dict.

        The dict is parsed by :func:`django.forms.utils.flatatt`,
        so:

        - ``{'myattribute': True}`` results in ``myattribute`` (no value).
        - ``{'myattribute': False}`` results in the attribute beeing ignored (not included in the output).
        - ``{'myattribute': 'Some value'}`` results in the ``myattribute="Some value"``.

        If you override this method, *remember to call super* to get
        the attributes set in the superclass.
        """
        html_element_attributes = {
            "role": self.role,
            "id": self.dom_id,
            "class": self.css_classes or False,  # Fall back to false to avoid class=""
        }
        if self._html_element_attributes:
            html_element_attributes.update(self._html_element_attributes)
        return html_element_attributes

    @property
    def html_element_attributes_string(self):
        """
        Get :meth:`.get_html_element_attributes` + any attributes in
        the ``html_element_attributes`` kwarg for :meth:`.__init__`
        encoded as a string using :func:`django.forms.utils.flatatt`.
        """
        return flatatt(self.get_html_element_attributes())

    def get_default_css_classes_list(self):
        """
        Override this to provide a default list of css classes.

        The css classes specified here can be overridden using
        the ``css_classes_list`` kwarg for :meth:`.__init__`.
        """
        return []

    def get_default_bem_block_or_element(self):
        """
        Get the default BEM block or element.

        A HTML element is eighter a BEM block or a
        BEM element, so we have joined this into
        a single method.
        """
        return None

    def get_bem_block_or_element(self):
        """
        Get the BEM block or element.

        DO NOT OVERRIDE THIS METHOD.
        Override :meth:`.get_default_bem_block_or_element` instead.
        """
        return self._overridden_bem_block_or_element or self.get_default_bem_block_or_element()

    def get_default_bem_variant_list(self):
        """
        Get the default BEM variants.

        The full CSS class of any variant in the list will
        be :meth:`.get_bem_block_or_element` with ``--`` and
        the variant appended, so if the bem block/element is
        ``"menu"``, and the variant is ``"expanded"``, the
        resulting css class will be ``"menu--expanded"``.
        """
        return []

    def get_bem_variant_list(self):
        """
        Get the list of BEM variants.

        DO NOT OVERRIDE THIS METHOD.
        Override :meth:`.get_default_bem_variant_list` instead.
        """
        return self._overridden_bem_variant_list or self.get_default_bem_variant_list()

    def get_bem_css_classes_list(self):
        """
        Get the BEM css classes as list.

        DO NOT OVERRIDE THIS METHOD.
        Override :meth:`.get_default_bem_block_or_element`
        and :meth:`.get_default_bem_variant_list` instead.
        """
        bem_block_or_element = self.get_bem_block_or_element()
        bem_css_classes = []
        if bem_block_or_element:
            bem_css_classes.append(bem_block_or_element)
            for variant in self.get_bem_variant_list():
                css_class = "{}--{}".format(bem_block_or_element, variant)
                bem_css_classes.append(css_class)
        return bem_css_classes

    def get_css_classes_list(self):
        """
        DO NOT OVERRIDE THIS METHOD.

        Unlike with :class:`django_cradmin.renderable.AbstractRenderableWithCss`,
        you do not override this class to add your own css classes. Override
        :meth:`.get_default_css_classes_list`.

        This is because this method respects the ``css_classes_list`` kwarg
        for :meth:`.__init__`, and just falls back to :meth:`.get_default_css_classes_list`.
        So if you override this method, the ``css_classes_list`` kwarg will be useless.
        """
        css_classes_list = self.get_bem_css_classes_list()
        if self._overridden_css_classes_list:
            css_classes_list.extend(self._overridden_css_classes_list)
        else:
            css_classes_list.extend(self.get_default_css_classes_list())
        if self._extra_css_classes_list:
            css_classes_list.extend(self._extra_css_classes_list)
        return css_classes_list

    def get_default_test_css_class_suffixes_list(self):
        """
        Override this to provide a default list of css classes for unit tests.

        The css classes specified here can be overridden using
        the ``test_css_class_suffixes_list`` kwarg for :meth:`.__init__`.
        """
        return ["uicontainer-{}".format(self.__class__.__name__.lower())]

    def get_test_css_class_suffixes_list(self):
        """
        DO NOT OVERRIDE THIS METHOD.

        Unlike with :class:`django_cradmin.renderable.AbstractRenderableWithCss`,
        you do not override this class to add your own test css classes. Override
        :meth:`.get_default_test_css_class_suffixes_list`.

        This is because this method respects the ``test_css_class_suffixes_list`` kwarg
        for :meth:`.__init__`, and just falls back to :meth:`.get_default_test_css_class_suffixes_list`.
        So if you override this method, the ``test_css_class_suffixes_list`` kwarg will be useless.
        """
        if self._overridden_test_css_class_suffixes_list:
            test_css_class_suffixes_list = self._overridden_test_css_class_suffixes_list
        else:
            test_css_class_suffixes_list = self.get_default_test_css_class_suffixes_list()
        return test_css_class_suffixes_list

    def bootstrap(self, parent=None):
        """
        Bootstrap the container.

        Must be called once on the top-level container
        in the tree of containers.

        Sets the provided parent as :attr:`.parent`.

        Updates the properties of all children (using dict update())
        with :attr:`.properties`.
        """
        if self._is_bootstrapped:
            raise AlreadyBootsrappedError(
                "The container is already bootstrapped. Can not bootstrap the same container twice."
            )
        self.parent = parent
        if self.parent:
            self.properties.update(self.parent.properties)
        for child in self._virtual_childrenlist:
            child.bootstrap(parent=self)
        for child in self._childrenlist:
            child.bootstrap(parent=self)
        self._is_bootstrapped = True
        return self

    def prepopulate_children_list(self):
        """
        Pre-polulate the children list.

        This is called in :meth:`.__init__` before
        any children from the kwargs is added.

        Returns:
            list: An empty list by default, but you can override this
            in subclasses.
        """
        return []

    def prepopulate_virtual_children_list(self):
        """
        Pre-polulate the virtual children list.

        This is called in :meth:`.__init__` before
        any children from the kwargs is added, and before any children
        is :meth:`.prepopulate_children_list` is added.

        Returns:
            list: An empty list by default, but you can override this
            in subclasses.
        """
        return []

    def add_child(self, childcontainer):
        """
        Add a child to the container.

        Args:
            childcontainer: A :class:`.AbstractContainerRenderable` object.

        Returns:
            A reference to self. This means that you can chain calls to this method.
        """
        if self.can_have_children:
            self._childrenlist.append(childcontainer)
            if self._is_bootstrapped and not childcontainer._is_bootstrapped:
                childcontainer.bootstrap(parent=self)
        else:
            raise NotAllowedToAddChildrenError(
                "{modulename}.{classname} can not have children".format(
                    modulename=self.__class__.__module__, classname=self.__class__.__name__
                )
            )
        return self

    def add_virtual_child(self, childcontainer):
        """
        Add a "virtual" child to the container.

        This child is not rendered as a child of the container automatically
        (that is left to the template rendering the container). But it
        inherits properties and is automatically bootstrapped just like a
        regular child.

        Args:
            childcontainer: A :class:`.AbstractContainerRenderable` object.
        Returns:
            A reference to self. This means that you can chain calls to this method.
        """
        if self.can_have_children:
            self._virtual_childrenlist.append(childcontainer)
            if self._is_bootstrapped and not childcontainer._is_bootstrapped:
                childcontainer.bootstrap(parent=self)
        return self

    def add_children(self, *childcontainers):
        """
        Add children to the container.

        Args:
            *childcontainers: Zero or more :class:`.AbstractContainerRenderable` objects.

        Returns:
            A reference to self. This means that you can chain calls to this method.
        """
        for childcontainer in childcontainers:
            self.add_child(childcontainer)
        return self

    def add_virtual_children(self, *childcontainers):
        """
        Add virtual children to the container.

        Args:
            *childcontainers: Zero or more :class:`.AbstractContainerRenderable` objects.

        Returns:
            A reference to self. This means that you can chain calls to this method.
        """
        for childcontainer in childcontainers:
            self.add_virtual_child(childcontainer)
        return self

    def iter_children(self):
        """
        Returns an iterator over the children of this container.

        The yielded children will be objects of :class:`.AbstractContainerRenderable`
        subclasses.
        """
        return iter(self._childrenlist)

    def iter_virtual_children(self):
        """
        Returns an iterator over the virtual children of this container.

        The yielded children will be objects of :class:`.AbstractContainerRenderable`
        subclasses.
        """
        return iter(self._virtual_childrenlist)

    def get_childcount(self):
        """
        Get the number of children in the container.
        """
        return len(self._childrenlist)

    def get_virtual_childcount(self):
        """
        Get the number of virtual children in the container.
        """
        return len(self._virtual_childrenlist)

    @property
    def should_render(self):
        """
        Should we render anything?

        Override this to make the :meth:`.render` to control
        if the container is rendered. If this returns ``False``,
        :meth:`.render` returns an empty string instead of
        rendering the template.

        Returns:
            bool: ``True`` by default, but subclasses can override this behavior.
        """
        return True

    def render(self, **kwargs):
        """
        Overrides :meth:`django_cradmin.renderable.AbstractRenderable.render`.
        The only change is that we return an empty string if
        :meth:`.should_render` returns ``False``. If it returns ``True``,
        we call the overriden method and returns the result.

        Args:
            **kwargs: Forwarded to the overridden method if it is called.
        """
        if not self._is_bootstrapped:
            raise NotBootsrappedError(
                "Can not render an AbstractContainerRenderable that has not been bootstrapped. "
                "Ensure you call bootsrap() on the top-level container in the container "
                "hierarchy before rendering. Class causing this issue: {classpath}".format(
                    classpath=self.get_full_class_path_as_string()
                )
            )
        if self.should_render:
            return super(AbstractContainerRenderable, self).render(**kwargs)
        else:
            return ""


class Div(AbstractContainerRenderable):
    """
    Renders a ``<div>``.

    The only thing this class does is to override
    :meth:`django_cradmin.uicontainer.container.AbstractContainerRenderable.get_default_html_tag`
    and return ``"div"``.
    """

    def get_default_html_tag(self):
        return "div"


class NoWrapperElement(AbstractContainerRenderable):
    """
    Renders children, but no wrapper HTML element.
    """

    template_name = "django_cradmin/uicontainer/no_wrapper_element.django.html"
