from os.path import exists, join
from os import listdir

from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import classonlymethod
from django.conf.urls.defaults import url

from devilry.utils.importutils import get_staticdir_from_appname


class JsAppView(View):
    appname = None
    templatename = 'production'
    with_css = False
    include_old_exjsclasses = False
    libs = []

    @classonlymethod
    def as_appview(cls, appname, **kwargs):
        return cls.as_view(appname=appname, **kwargs)

    def get_base(self, request, **extra):
        kw = {'appname': self.appname,
              'with_css': self.with_css,
              'libs': self.libs,
              'include_old_exjsclasses': self.include_old_exjsclasses}
        kw.update(extra)
        return render(request, 'jsapp/{0}.django.html'.format(self.templatename), kw)

    def get(self, request):
        return self.get_base(request)


class JsAppTestView(JsAppView):
    templatename = 'test'


class JsAppJasmineTestView(JsAppTestView):
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


def create_urls(appname, with_css=False, libs=[], include_old_exjsclasses=False):
    kwargs = dict(with_css=with_css, libs=libs, include_old_exjsclasses=include_old_exjsclasses)
    return (url(r'^ui$', login_required(JsAppView.as_appview(appname, **kwargs))),
            url(r'^test$', JsAppTestView.as_appview(appname, **kwargs)),
            url(r'^jasminetest$', JsAppJasmineTestView.as_appview(appname, **kwargs)))
