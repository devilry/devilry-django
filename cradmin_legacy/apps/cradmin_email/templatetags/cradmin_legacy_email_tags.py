from django import template
from django.template.loader import render_to_string

register = template.Library()


def _cradmin_email_buttonlink(parser, token, linkstyle_context_variable):
    try:
        tag_name, url = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly one arguments" % token.contents.split()[0])
    end_tag = f"end_{tag_name}"
    nodelist = parser.parse((end_tag,))
    parser.delete_first_token()
    return CradminEmailButtonlinkNode(nodelist=nodelist, url=url, linkstyle_context_variable=linkstyle_context_variable)


class CradminEmailButtonlinkNode(template.Node):
    def __init__(self, nodelist, url, linkstyle_context_variable):
        if url[0] in ('"', "'"):
            url = url[1:-1]
        else:
            # Assume we have a variable
            url = template.Variable(url)
        self.url = url
        self.nodelist = nodelist
        self.linkstyle_context_variable = linkstyle_context_variable

    def render(self, context):
        output = self.nodelist.render(context)

        if isinstance(self.url, template.Variable):
            url = self.url.resolve(context)
        else:
            url = self.url
        linkstyle = context.get(self.linkstyle_context_variable, "")
        return render_to_string(
            "cradmin_email/templatetags/cradmin_email_buttonlink.django.html",
            {"url": url, "label": output, "linkstyle": linkstyle},
        )


@register.tag
def cradmin_email_primary_buttonlink(parser, token):
    """
    Render a link as a primary button.

    Examples::

        Url as string:

        .. code-block:: htmldjango

            {% load cradmin_legacy_email_tags %}
            {% cradmin_email_primary_buttonlink "http://example.com" %}
                A primary button link
            {% end_cradmin_email_primary_buttonlink %}

        Url as context variable:

        .. code-block:: htmldjango

            {% load cradmin_legacy_email_tags %}
            {% cradmin_email_primary_buttonlink someurl %}
                A primary button link
            {% end_cradmin_email_primary_buttonlink %}
    """
    return _cradmin_email_buttonlink(parser, token, linkstyle_context_variable="primary_button_link_style")


@register.tag
def cradmin_email_secondary_buttonlink(parser, token):
    """
    Render a link as a secondary button.

    Examples::

        Url as string:

        .. code-block:: htmldjango

            {% load cradmin_legacy_email_tags %}
            {% cradmin_email_secondary_buttonlink "http://example.com" %}
                A secondary button link
            {% end_cradmin_email_secondary_buttonlink %}

        Url as context variable:

        .. code-block:: htmldjango

            {% load cradmin_legacy_email_tags %}
            {% cradmin_email_secondary_buttonlink someurl %}
                A secondary button link
            {% end_cradmin_email_primary_buttonlink %}
    """
    return _cradmin_email_buttonlink(parser, token, linkstyle_context_variable="secondary_button_link_style")
