import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from django.http import HttpResponse
from django.template import loader, Context



class XmlRpcDispatcher(SimpleXMLRPCDispatcher):
    def _marshaled_dispatch(self, data, request):
        """Dispatches an XML-RPC method from marshalled (XML) data.

        This is a copy of SimpleXMLRPCDispatcher._marshaled_dispatch, but with
        the `dispatch_method`-argument removed, and the `request`-argument added.

        The motivation for this method is to make the django HttpRequest object
        available as the first parameter to all xmlrpc-functions.

        :param request: A django.http.HttpRequest object.
        """
        try:
            params, method = xmlrpclib.loads(data)

            # generate response
            p = [request]
            p.extend(params)
            response = self._dispatch(method, p)

            # wrap response in a singleton tuple
            response = (response,)
            response = xmlrpclib.dumps(response, methodresponse=1,
                    allow_none=self.allow_none, encoding=self.encoding)
        except Fault, fault:
            response = xmlrpclib.dumps(fault, allow_none=self.allow_none,
                    encoding=self.encoding)
        except:
            # report exception back to server
            exc_type, exc_value, exc_tb = sys.exc_info()
            response = xmlrpclib.dumps(
                xmlrpclib.Fault(1, "%s:%s" % (exc_type, exc_value)),
                encoding=self.encoding, allow_none=self.allow_none,
                )

        return response


class XmlRpc(object):
    def __init__(self):
        self.dispatcher = XmlRpcDispatcher()

    def __call__(self, request):
        """Dispatch XML-RPC requests."""
        if request.method == 'POST':
            # XMLRPC
            response = HttpResponse(mimetype='text/xml')
            result = self.dispatcher._marshaled_dispatch(request.raw_post_data, request)
            response.write(result)
            response['Content-length'] = str(len(response.content))
            return response
        else:
            # Documentation
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
