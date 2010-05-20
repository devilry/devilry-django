from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from django.http import HttpResponse
from django.template import loader, Context

dispatcher = SimpleXMLRPCDispatcher()
                                                                                
def call_xmlrpc(request):
    """Dispatch XML-RPC requests."""
    if request.method == 'POST':
        # Process XML-RPC call
        response = HttpResponse(mimetype='text/xml')
        response.write(dispatcher._marshaled_dispatch(request.raw_post_data))
        response['Content-length'] = str(len(response.content))
        return response
    else:
        # Show documentation on available methods
        response = HttpResponse()
        t = loader.get_template('devilry/xmlrpc/documentation.html')
        docs = [(m, dispatcher.system_methodHelp(m)) for m in dispatcher.system_listMethods()]
        c = Context({'docs': docs})
        response.write(t.render(c))
        return response

def xmlrpc(uri):
    """A decorator for XML-RPC functions."""
    def register_xmlrpc(fn):
        dispatcher.register_function(fn, uri)
        return fn
    return register_xmlrpc


@xmlrpc('example.sum')
def sum(a, b):
    """ Returns the sum of *a* and *b*. """
    return a + b
