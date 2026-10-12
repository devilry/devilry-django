from django.template.loader import render_to_string

0


class AbstractRenderable:
    """
    An abstract class that implements an interface for
    rendering something.

    Everything is just helpers for the :meth:`.render` method,
    which renders a template with an object of this class as
    input.
    """

    template_name = None

    def get_template_name(self):
        """
        Get the template name for :meth:`.render`.

        Defaults to :obj:`~.AbstractRenderable.template_name`.

        Raises:
            NotImplementedError: If :obj:`~.AbstractRenderable.template_name` is
             not set.
        """
        if self.template_name:
            return self.template_name
        else:
            raise NotImplementedError("You must set template_name or override get_template_name().")

    def get_context_data(self, request=None):
        """
        Get context data for :meth:`.render`.

        Defaults to::

            {
                'me': self
            }
        """
        return {"me": self}

    def render(self, request=None):
        """
        Render :obj:`.get_template_name` with
        the context returned by :meth:`.get_context_data`.

        Paramteters:
            request (HttpRequest): If this is provided, we forward it to
                :meth:`.get_context_data`, and to ``render_to_string()``
                (which is used to render the template).
        """
        context = self.get_context_data(request=request)
        return render_to_string(self.get_template_name(), context, request=request)


class AbstractRenderableWithCss(AbstractRenderable):
    """
    Extends :class:`.AbstractRenderable` with a unified
    API for setting CSS classes.
    """

    def get_extra_css_classes_list(self):
        """
        Override this to set your own css classes. Must return a list
        of css classes.

        This is reserved for setting css classes when extending a
        reusable component.

        See :meth:`.get_css_classes_string`.
        """
        return []

    def get_base_css_classes_list(self):
        """
        If you are creating a reusable component, use this to
        define css classes that should always be present on
        the component. When developers extend your re-usable
        component, they should override :meth:`.get_extra_css_classes`.

        Must return a list of css classes.

        See :meth:`.get_css_classes_string`.
        """
        return []

    def get_css_classes_string(self):
        """
        Get css classes.

        Joins :meth:`.get_base_css_classes` with :meth:`.get_extra_css_classes` into a string.

        You should not override this:

        - Override :meth:`.get_extra_css_classes` if you are extending a reusable component.
        - Override :meth:`.get_base_css_classes` if you are creating a reusable component.
        """
        css_classes = []
        css_classes.extend(self.get_base_css_classes_list())
        css_classes.extend(self.get_extra_css_classes_list())
        return " ".join(css_classes)
