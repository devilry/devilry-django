import xmlrpclib
import textwrap
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher

from django.http import HttpResponse
from django.template import loader, Context
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse




def normalize_docstring(docstring):
    """ Prepare docstring for parsing by the django 'restructuredtext'
    filter.
    """
    doc = docstring.split('\n')
    first_line = doc[0].strip()
    rest = textwrap.dedent('\n'.join(doc[1:]))
    return first_line + '\n' + rest

class XmlRpc(object):
    xmlrpcs = {}

    def __init__(self, name, viewname):
        if name in self.__class__.xmlrpcs:
            raise ValueError("'%s' is already registered as a XmlRpc." % name)
        self.name = name
        self.viewname = viewname
        self.__class__.xmlrpcs[name] = self
        self.dispatch = {}


    def get_url(self):
        return reverse(self.viewname)

    def xmlrpc_request(self, request):
        p, u = xmlrpclib.getparser()
        p.feed(request.raw_post_data)
        p.close()
        args = u.close()
        method = u.getmethodname()
        func = self.dispatch.get(method)
        if func is not None:
            try:
                result = func(request, *args)
                xml = xmlrpclib.dumps((result,), methodresponse=1,
                        allow_none=True)
            except Exception, e:
                xml = xmlrpclib.dumps(
                        xmlrpclib.Fault(-32400, 'system error: %s' % e),
                        methodresponse=1)
        else:
            xml = xmlrpclib.dumps(
                    xmlrpclib.Fault(-32601, 'method unknown: %s' % method),
                    methodresponse=1)

        return HttpResponse(xml, mimetype='text/xml; charset=utf-8')

    def htmldocs(self, request):
        docs = [(name, normalize_docstring(f.__doc__))
                for name, f in self.dispatch.iteritems()]
        return render_to_response('devilry/xmlrpc/xmlrpcdoc.django.html', {
            'name': self.name,
            'docs': docs,
            'xmlrpcs': self.__class__.xmlrpcs
            }, context_instance=RequestContext(request))

    def __call__(self, request):
        if request.method == 'POST':
            return self.xmlrpc_request(request)
        else:
            return self.htmldocs(request)

    def rpcdec(self, name=None):
        """ A decorator for XML-RPC functions.
        
        :param name: The name of the exported xmlrpc function. If None, the
                     function name is used.
        :type name: str or None
        """
        def register_xmlrpc(func):
            self.dispatch[name or func.__name__] = func
            return func
        return register_xmlrpc
