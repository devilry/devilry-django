from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import classonlymethod
from django.conf.urls.defaults import url


class GuiBaseView(View):
    appname = None
    templatename = None

    @classonlymethod
    def as_appview(cls, appname, templatename='production'):
        return cls.as_view(appname=appname, templatename=templatename)

    def get(self, request):
        return render(request, 'guibase/{0}.django.html'.format(self.templatename),
                      {'appname': self.appname})



def create_urls(appname):
    return (url(r'^ui$', login_required(GuiBaseView.as_appview(appname=appname))),
            url(r'^test$', GuiBaseView.as_appview(appname=appname, templatename='test')))
