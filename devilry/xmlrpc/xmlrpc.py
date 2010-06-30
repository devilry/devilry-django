import xmlrpclib
import textwrap

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required



class RpcFuncInfo(object):
    def __init__(self, func, argnames, constraints):
        self.name = func.__name__
        self.func = func
        self.argnames = argnames
        self.constraints = constraints

    def get_docstring(self):
        doc = self.func.__doc__.split('\n')
        first_line = doc[0].strip()
        rest = textwrap.dedent('\n'.join(doc[1:]))
        return first_line + '\n' + rest


class XmlRpc(object):
    """ Represents a xmlrpc. """
    xmlrpcs = {}

    def __init__(self, name, viewname, docs=''):
        """
        Raises ``ValueError`` if *name* is not unique.

        :param name:
            A unique name for this xmlrpc.
        :param viewname:
            Name of the view (you define this when you add the object to
            your urls. Must be something that
            ``django.core.urlresolvers.reverse`` can handle.
        :param docs:
            A reStructuredText string displayed at the top of the HTML
            documentation.
        """
        self.argnames = {}
        if name in self.__class__.xmlrpcs:
            raise ValueError("'%s' is already registered as a XmlRpc." % name)
        self.name = name
        self.docs = docs
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
        funcinfo = self.dispatch.get(method)
        if funcinfo is not None:
            func = funcinfo.func
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
        return render_to_response('devilry/xmlrpc/xmlrpcdoc.django.html', {
            'name': self.name,
            'docs': self.docs,
            'funcinfo': self.dispatch.values(),
            'xmlrpcs': self.__class__.xmlrpcs
            }, context_instance=RequestContext(request))

    def __call__(self, request):
        if request.method == 'POST':
            return self.xmlrpc_request(request)
        else:
            return self.htmldocs(request)

    def rpcdec(self, argnames="", constraints=[]):
        """ A decorator for XML-RPC functions.
        
        **Note**: the arguments are only for documentation.

        :param argnames:
            A string containing arguments for the html documentation.
        :param constraints:
            A list informing the user of extra constraints, like required
            permissions.
        """
        def register_xmlrpc(func):
            self.dispatch[func.__name__] = RpcFuncInfo(func, argnames,
                    constraints)
            return func
        return register_xmlrpc

    def rpcdec_login_required(self, argnames="", constraints=[]):
        """ Shortcut for::
            
            @rpcdec(argnames, ['Login required'])
            @django.contrib.auth.decorators.login_required

        Note that the constraint, 'Login requred', is inserted first in
        constraints, so you can add more constrains just like with
        :ref:`rpcdec`.
        """
        constraints = ['Login required'] + constraints
        def register_xmlrpc(func):
            f = login_required(func)
            self.dispatch[func.__name__] = RpcFuncInfo(f, argnames,
                    constraints)
            return f
        return register_xmlrpc
