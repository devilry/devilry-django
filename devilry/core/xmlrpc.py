from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from django.http import HttpResponse
from django.template import loader, Context


class XmlRpc(object):
    def __init__(self):
        self.dispatcher = SimpleXMLRPCDispatcher()

    def __call__(self, request):
        """Dispatch XML-RPC requests."""
        if request.method == 'POST':
            # Process XML-RPC call
            response = HttpResponse(mimetype='text/xml')
            response.write(self.dispatcher._marshaled_dispatch(request.raw_post_data))
            response['Content-length'] = str(len(response.content))
            return response
        else:
            # Show documentation on available methods
            response = HttpResponse()
            t = loader.get_template('devilry/ui/xmlrpcdoc.django.html')
            docs = [(m, self.dispatcher.system_methodHelp(m))
                    for m in self.dispatcher.system_listMethods()]
            c = Context({'docs': docs})
            response.write(t.render(c))
            return response

    def rpcdec(self, name=None):
        """ A decorator for XML-RPC functions.
        
        :param name: The name of the exported xmlrpc function. If None, the
                     function name is used.
        :type name: str or None
        """
        def register_xmlrpc(fn):
            self.dispatcher.register_function(fn, name or fn.__name__)
            return fn
        return register_xmlrpc
