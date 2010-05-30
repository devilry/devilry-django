import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from django.http import HttpResponse
from django.template import loader, Context


class XmlRpc(object):
    def __init__(self):
        self.dispatch = {}

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
                xml = xmlrpclib.dumps((result,), methodresponse=1)
            except Exception, e:
                xml = xmlrpclib.dumps(xmlrpclib.Fault(-32400, 'system error: %s' % e), methodresponse=1)
        else:
            xml = xmlrpclib.dumps(xmlrpclib.Fault(-32601, 'method unknown: %s' % method), methodresponse=1)

        return HttpResponse(xml, mimetype='text/xml; charset=utf-8')

    def htmldocs(self, request):
        response = HttpResponse()
        t = loader.get_template('devilry/ui/xmlrpcdoc.django.html')
        docs = [(name, f.__doc__)
                for name, f in self.dispatch.iteritems()]
        c = Context({'docs': docs})
        response.write(t.render(c))
        return response

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
