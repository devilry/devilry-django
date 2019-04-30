import sys
import cProfile
from io import StringIO
import pstats

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class ProfilerMiddleware(MiddlewareMixin):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if settings.DEBUG and 'prof' in request.GET:
            self.profiler = cProfile.Profile()
            args = (request,) + callback_args
            return self.profiler.runcall(callback, *args, **callback_kwargs)

    def process_response(self, request, response):
        if settings.DEBUG and 'prof' in request.GET:
            self.profiler.create_stats()

            outfile = "profile/stats.dump"
            self.profiler.dump_stats(outfile)

            out = StringIO()
            p = pstats.Stats(outfile, stream=out)
            #p.strip_dirs()
            p.sort_stats('cumulative')
            p.print_stats(-1)
            response.content = '<pre>%s</pre>' % out.getvalue()
        return response

