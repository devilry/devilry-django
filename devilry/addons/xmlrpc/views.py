from devilry.core.xmlrpc import XmlRpc

rpc = XmlRpc()


@rpc.rpcdec()
def sum(a, b):
    """ Returns the sum of *a* and *b*. """
    return a + b
