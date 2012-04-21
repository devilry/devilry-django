"""
Post processors for ouput data from REST methods.
"""
from utils import request_is_extjs

def extjs(request, output_data, success):
    """
    Adds the data required by ``extjs`` to the response if :func:`~.utils.request_is_extjs`.

    If the output_data is a ``dict``, it adds the ``success`` key to
    ``output_data``.

    If ``output_data`` is ``None``, it returns ``{"success": success}``
    as output_data.
    """
    if request_is_extjs(request):
        if isinstance(output_data, dict):
            output_data['success'] = success
        elif output_data == None:
            output_data = dict(success=success)
        return True, output_data
    return False, None
