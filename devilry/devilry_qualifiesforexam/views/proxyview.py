from django.views.generic import View


class PageProxyView(View):
    def get_urlpath(self):
        urlpath = self.kwargs.get('urlpath', '')
        urlpath = '/' + urlpath
        urlpath = urlpath.rstrip('/')
        return urlpath
