import json

from django import template
from django.conf import settings
from django.templatetags.static import static
import warnings

from cradmin_legacy import crapp
from cradmin_legacy.crinstance import reverse_cradmin_url
from cradmin_legacy.registry import cradmin_instance_registry

register = template.Library()


@register.simple_tag(takes_context=True)
def cradmin_titletext_for_role(context, role):
    """
    Template tag implementation of
    :meth:`cradmin_legacy.crinstance.BaseCrAdminInstance.get_titletext_for_role`.
    """
    request = context["request"]
    cradmin_instance = cradmin_instance_registry.get_current_instance(request)
    return cradmin_instance.get_titletext_for_role(role)


@register.simple_tag(takes_context=True)
def cradmin_descriptionhtml_for_role(context, role):
    """
    Template tag implementation of
    :meth:`cradmin_legacy.crinstance.BaseCrAdminInstance.get_titletext_for_role`.
    """
    request = context["request"]
    cradmin_instance = cradmin_instance_registry.get_current_instance(request)
    return cradmin_instance.get_descriptionhtml_for_role(role)


@register.simple_tag(takes_context=True)
def cradmin_rolefrontpage_url(context, role):
    """
    Template tag implementation of
    :meth:`cradmin_legacy.crinstance.BaseCrAdminInstance.rolefrontpage_url`.
    """
    request = context["request"]
    cradmin_instance = cradmin_instance_registry.get_current_instance(request)
    return cradmin_instance.rolefrontpage_url(cradmin_instance.get_roleid(role))


@register.simple_tag(takes_context=True)
def cradmin_appurl(context, viewname, *args, **kwargs):
    """
    Template tag implementation of :meth:`cradmin_legacy.crapp.App.reverse_appurl`.

    Examples:

        Reverse the view named ``"edit"`` within the current app:

        .. code-block:: htmldjango

            {% load cradmin_legacy_tags %}

            <a href='{% cradmin_appurl "edit" %}'>Edit</a>

        Reverse a view with keyword arguments:

        .. code-block:: htmldjango

            {% load cradmin_legacy_tags %}

            <a href='{% cradmin_appurl "list" mode="advanced" orderby="name" %}'>
                Show advanced listing ordered by name
            </a>
    """
    request = context["request"]
    return request.cradmin_app.reverse_appurl(viewname, args=args, kwargs=kwargs)


@register.simple_tag(takes_context=True)
def cradmin_appindex_url(context, *args, **kwargs):
    """
    Template tag implementation of :meth:`cradmin_legacy.crinstance.BaseCrAdminInstance.appindex_url`.

    Examples:

        Reverse index (frontpage) of current app:

        .. code-block:: htmldjango

            {% load cradmin_legacy_tags %}

            <a href='{% cradmin_appindex_url %}'>
                Go to pages-app
            </a>

        Reverse a view with keyword arguments:

        .. code-block:: htmldjango

            {% load cradmin_legacy_tags %}

            <a href='{% cradmin_appindex_url mode="advanced" orderby="name" %}'>
                Show advanced listing ordered by name
            </a>
    """
    request = context["request"]
    return request.cradmin_app.reverse_appurl(viewname=crapp.INDEXVIEW_NAME, args=args, kwargs=kwargs)


@register.simple_tag(takes_context=True)
def cradmin_instance_appindex_url(context, appname, *args, **kwargs):
    """
    Template tag implementation of :meth:`cradmin_legacy.crinstance.BaseCrAdminInstance.appindex_url`.

    Examples:

        Reverse index (frontpage) of the ``"pages"`` app:

        .. code-block:: htmldjango

            {% load cradmin_legacy_tags %}

            <a href='{% cradmin_instance_appindex_url appname="pages" %}'>
                Go to pages-app
            </a>

        Reverse a view with keyword arguments:

        .. code-block:: htmldjango

            {% load cradmin_legacy_tags %}

            <a href='{% cradmin_instance_appindex_url appname="pages" mode="advanced" orderby="name" %}'>
                Show advanced listing ordered by name
            </a>
    """
    request = context["request"]
    return request.cradmin_instance.reverse_url(
        appname=appname, viewname=crapp.INDEXVIEW_NAME, args=args, kwargs=kwargs
    )


@register.simple_tag(takes_context=True)
def cradmin_instanceindex_url(context, appname):
    warnings.warn(
        "cradmin_instanceindex_url is deprecated. Use cradmin_instance_appindex_url instead.", DeprecationWarning
    )
    return cradmin_instance_appindex_url(context, appname)


@register.simple_tag(takes_context=True)
def cradmin_instance_url(context, appname, viewname, *args, **kwargs):
    """
    Template tag implementation of :meth:`cradmin_legacy.crinstance.BaseCrAdminInstance.reverse_url`.

    Examples:

        Reverse the view named ``"edit"`` within the app named ``"pages"``:

        .. code-block:: htmldjango

            {% load cradmin_legacy_tags %}

            <a href='{% cradmin_instance_url appname="pages" viewname="edit" %}'>
                Edit
            </a>

        Reverse a view with keyword arguments:

        .. code-block:: htmldjango

            {% load cradmin_legacy_tags %}

            <a href='{% cradmin_instance_url appname="pages" viewname="list" mode="advanced" orderby="name" %}'>
                Show advanced pages listing ordered by name
            </a>
    """
    request = context["request"]
    return request.cradmin_instance.reverse_url(appname=appname, viewname=viewname, args=args, kwargs=kwargs)


@register.simple_tag(takes_context=True)
def cradmin_url(context, instanceid, appname, roleid, viewname, *args, **kwargs):
    """
    Template tag implementation of :meth:`cradmin_legacy.crinstance.reverse_cradmin_url`.

    Examples:

        Reverse the view named ``"edit"`` within the app named ``"pages"`` in the
        cradmin-instance with id ``"my_cradmin_instance"`` using roleid ``10``:

        .. code-block:: htmldjango

            {% load cradmin_legacy_tags %}

            <a href='{% cradmin_instance_url instanceid="my_cradmin_instance" appname="pages"
            roleid=10 viewname="edit" %}'>
                Edit
            </a>

        Reverse a view with keyword arguments:

        .. code-block:: htmldjango

            {% load cradmin_legacy_tags %}

            <a href='{% cradmin_instance_url instanceid="my_cradmin_instance" appname="pages"
            roleid=10 viewname="list" mode="advanced" orderby="name" %}'>
                Show advanced pages listing ordered by name
            </a>
    """
    return reverse_cradmin_url(
        instanceid=instanceid, appname=appname, roleid=roleid, viewname=viewname, args=args, kwargs=kwargs
    )


@register.simple_tag(takes_context=True)
def cradmin_render_menu(context):
    """
    Template tag that renders the cradmin menu.

    We use this instead of an include tag to handle some issues
    with mocking tests.
    """
    request = context["request"]
    if hasattr(request, "cradmin_instance"):
        return request.cradmin_instance.get_menu().render(context.flatten())
    return ""


@register.filter
def cradmin_jsonencode(json_serializable_pythonobject):
    """
    Template filter that converts a json serializable object
    to a json encoded string.
    """
    return json.dumps(json_serializable_pythonobject)


@register.simple_tag(takes_context=True)
def cradmin_theme_staticpath(context):
    """ """
    if "request" in context:
        request = context["request"]
        theme_path = None
        if hasattr(request, "cradmin_instance"):
            theme_path = request.cradmin_instance.get_cradmin_theme_path()
            if theme_path:
                theme_path = str(theme_path)
        if not theme_path:
            theme_path = getattr(
                settings, "CRADMIN_LEGACY_THEME_PATH", "cradmin_legacy/dist/css/cradmin_theme_default/theme.css"
            )
        return static(theme_path)
    else:
        return ""


@register.simple_tag(takes_context=True)
def cradmin_render_renderable(context, renderable):
    """
    Render a :class:`cradmin_legacy.renderable.AbstractRenderable`.

    Unlike just using ``{{ renderable.render }}``, this
    sends the ``request`` into render (so this is the same
    as calling ``renderable.render(request=context['request'])``.

    Examples:

        Render a renderable named ``renderable`` in the current template context:

        .. code-block:: htmldjango

            {% load cradmin_legacy_tags %}

            {% cradmin_render_renderable renderable %}
    """
    request = context.get("request", None)
    return renderable.render(request=request)
