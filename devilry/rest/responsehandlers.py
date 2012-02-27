"""
Response handlers are responsible for creating the response after the 
rest method has been successfully invoked, and the output has been encoded.
"""
from django.http import HttpResponse

def stricthttp(request, restapimethodname, output_content_type, encoded_output):
    """
    A response handler that respons with status ``201`` if
    ``restapimethodname`` and status ``200`` for any other
    ``restapimethodname``.
    """
    if restapimethodname == "create":
        status = 201
    else:
        status = 200
    return HttpResponse(encoded_output, content_type=output_content_type, status=status)
