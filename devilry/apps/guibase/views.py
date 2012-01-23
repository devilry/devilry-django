from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import classonlymethod
from django.conf.urls.defaults import url


class GuiBaseView(View):
    appname = None
    templatename = None
    with_css = False

    @classonlymethod
    def as_appview(cls, appname, templatename='production', with_css=False):
        return cls.as_view(appname=appname, templatename=templatename, with_css=with_css)

    def get(self, request):
        return render(request, 'guibase/{0}.django.html'.format(self.templatename),
                      {'appname': self.appname,
                       'with_css': self.with_css})



def create_urls(appname, with_css=False):
    return (url(r'^ui$', login_required(GuiBaseView.as_appview(appname=appname, with_css=with_css))),
            url(r'^test$', GuiBaseView.as_appview(appname=appname, templatename='test', with_css=with_css)))
