from os.path import exists, join
from os import listdir

from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import classonlymethod
from django.conf.urls.defaults import url

from devilry.utils.importutils import get_staticdir_from_appname


class JsAppView(View):
    """
    A view that uses ``jsapp/<templatename>.django.html`` as view, and sends
    all of the attributes below into the template.

    You normally do not use this directly, but rather use:

    - :func:`create_app_urls`
    - :func:`create_lib_urls`

    .. attribute:: appname

        The name of the application.

    .. attribute:: templatename

        Defaults to ``"production"``.

    .. attribute:: with_css

        Defaults to ``False``.
        Set this to ``True`` if your app provides custom styles, and
        add your styles to::

            <appdir>/static/<appname>/resources/stylesheets/<appname>.css

    .. attribute:: include_old_exjsclasses

        Defaults to ``False``.
        If this is ``True``, add the old ``static/extjs_classes`` map to the
        ExtJS ``devilry`` namespace to ``Ext.loader``.

    .. attribute:: libs

        List of *jsapp* libraries that this app depends on. For each libname in
        the list, add::

            '{{ lib }}': '{{ DEVILRY_STATIC_URL }}/{{ lib }}/lib'

        to the ``Ext.Loader`` paths.

    .. attribute:: apptype

        Should be ``"app"`` for jsapp applications, and ``"lib"`` for jsapp
        libraries. Defaults to ``"app"``. ``create_lib_urls`` overrides this
        and sets it to ``"lib"``.
    """
    appname = None
    templatename = 'production'
    with_css = False
    include_old_exjsclasses = False
    libs = []
    apptype = 'app'

    @classonlymethod
    def as_appview(cls, **kwargs):
        return cls.as_view(**kwargs)

    def get_base(self, request, **extra):
        kw = {'appname': self.appname,
              'with_css': self.with_css,
              'libs': self.libs,
              'apptype': self.apptype,
              'include_old_exjsclasses': self.include_old_exjsclasses}
        kw.update(extra)
        return render(request, 'jsapp/{0}.django.html'.format(self.templatename), kw)

    def get(self, request):
        return self.get_base(request)


class JsAppTestView(JsAppView):
    """
    Overrides ``templatename`` to ``"test"``.
    """
    templatename = 'test'


class JsAppJasmineTestView(JsAppTestView):
    """
    Overrides ``templatename`` to ``"jasminetest"``, and adds all files in
    ``<appdir>/static/<appname>/jasminespecs/`` to the ``jasminespecs``
    template variable, which in turn is added to the jasmine test suite by the
    template.
    """
    templatename = 'jasminetest'
    def _get_jasmine_specs(self):
        staticdir = get_staticdir_from_appname(self.appname)
        jasminedir = join(staticdir, 'jasminespecs')
        if exists(jasminedir):
            return [filename for filename in listdir(jasminedir)
                    if filename.endswith('.js')]
        else:
            return []

    def get(self, request):
        return self.get_base(request, jasminespecs=self._get_jasmine_specs())


def create_app_urls(**kwargs):
    """
    Create views for applications. Forwards ``kwargs`` to:

    - :class:`JsAppView` (mapped to /ui)
    - :class:`JsAppTestView` (mapped to /test)
    - :class:`JsAppJasmineTestView` (mapped to /jasminetest)
    """
    return (url(r'^ui$', login_required(JsAppView.as_appview(**kwargs))),
            url(r'^test$', JsAppTestView.as_appview(**kwargs)),
            url(r'^jasminetest$', JsAppJasmineTestView.as_appview(**kwargs)))

def create_lib_urls(**kwargs):
    """
    Mostly the same as :func:`create_app_urls`, however it does not add ``/ui``, and
    ``apptype`` is automatically set to ``"lib"``.
    """
    kwargs['apptype'] = 'lib'
    return (url(r'^test$', JsAppTestView.as_appview(**kwargs)),
            url(r'^jasminetest$', JsAppJasmineTestView.as_appview(**kwargs)))
