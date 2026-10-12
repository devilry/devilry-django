from django_cradmin.uicontainer.container import AbstractContainerRenderable

from . import convenience


class Paragraph(convenience.AbstractWithOptionalEscapedText):
    """
    Renders a ``<p>``.
    """

    def get_default_html_tag(self):
        return "p"


class Link(convenience.AbstractWithOptionalEscapedText):
    """
    Renders a ``<a>``.
    """

    def __init__(self, href=False, target=False, **kwargs):
        """

        Args:
            href: The href attribute value. If this is ``False``
                (the default), no href attribute is rendered.
            target: The target attribute value. If this is ``False``
                (the default), no target attribute is rendered.
            **kwargs: Kwargs for :class:`django_cradmin.uicontainer.convenience.AbstractWithOptionalEscapedText`.
        """
        self.href = href
        self.target = target
        super(Link, self).__init__(**kwargs)

    def get_default_html_tag(self):
        return "a"

    def get_html_element_attributes(self):
        attributes = super(Link, self).get_html_element_attributes()
        attributes["href"] = self.href
        attributes["target"] = self.target
        return attributes


class Strong(convenience.AbstractWithOptionalEscapedText):
    """
    Renders a ``<strong>``.
    """

    def get_default_html_tag(self):
        return "strong"


class Em(convenience.AbstractWithOptionalEscapedText):
    """
    Renders a ``<em>``.
    """

    def get_default_html_tag(self):
        return "em"


class H1(convenience.AbstractWithOptionalEscapedText):
    """
    Renders a ``<h1>``.
    """

    def get_default_html_tag(self):
        return "h1"


class H2(convenience.AbstractWithOptionalEscapedText):
    """
    Renders a ``<h2>``.
    """

    def get_default_html_tag(self):
        return "h2"


class H3(convenience.AbstractWithOptionalEscapedText):
    """
    Renders a ``<h3>``.
    """

    def get_default_html_tag(self):
        return "h3"


class H4(convenience.AbstractWithOptionalEscapedText):
    """
    Renders a ``<h4>``.
    """

    def get_default_html_tag(self):
        return "h4"


class Section(AbstractContainerRenderable):
    """
    Renders a ``<section>``.
    """

    def get_default_html_tag(self):
        return "section"


class Header(AbstractContainerRenderable):
    """
    Renders a ``<header>``.
    """

    def get_default_html_tag(self):
        return "header"


class Footer(AbstractContainerRenderable):
    """
    Renders a ``<footer>``.
    """

    def get_default_html_tag(self):
        return "footer"


class Main(AbstractContainerRenderable):
    """
    Renders a ``<main>``.
    """

    def get_default_html_tag(self):
        return "main"

    def get_default_role(self):
        return "main"


class Nav(AbstractContainerRenderable):
    """
    Renders a ``<nav>``.
    """

    def get_default_html_tag(self):
        return "nav"


class Ul(AbstractContainerRenderable):
    """
    Renders a ``<ul>``.
    """

    def get_default_html_tag(self):
        return "ul"


class Ol(AbstractContainerRenderable):
    """
    Renders a ``<ol>``.
    """

    def get_default_html_tag(self):
        return "ol"


class Li(convenience.AbstractWithOptionalEscapedText):
    """
    Renders a ``<li>``.
    """

    def get_default_html_tag(self):
        return "li"
