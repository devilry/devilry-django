"""
Response handlers are responsible for creating the response after the 
rest method has been successfully invoked, and the output has been encoded.
"""
from django.http import HttpResponse

from error import ClientErrorBase


def clienterror(request, restapimethodname, output_content_type, encoded_output, error):
    """
    A response handler that checks if ``error`` is a
    :exc:`.error.ClientErrorBase` object, and if that is the case, a
    ``HttpResponse`` using ``error.STATUS`` is returned.
    """
    if error and isinstance(error, ClientErrorBase):
        return HttpResponse(encoded_output, content_type=output_content_type,
                            status=error.STATUS)
    else:
        return None

def stricthttp(request, restapimethodname, output_content_type, encoded_output, error):
    """
    A response handler that responds with status ``201`` if
    ``restapimethodname`` and status ``200`` for any other
    ``restapimethodname``.
    """
    if restapimethodname == "create":
        status = 201
    else:
        status = 200
    return HttpResponse(encoded_output, content_type=output_content_type,
                        status=status)
