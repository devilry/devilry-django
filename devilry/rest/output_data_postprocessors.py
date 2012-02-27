"""
Post processors for ouput data from REST methods.
"""

def extjs(request, output_data, successful):
    """
    Adds the data required by ``extjs`` to the response if one of the following
    conditions are met:

        - ``_devilry_extjs`` is in the querystring (request.GET).
        - The ``X_DEVILRY_USE_EXTJS`` HTTP header is in the request.

    What it actually does:

    - If the output_data is a ``dict``, it adds the ``successful`` key to
      ``output_data``.
    - If ``output_data`` is ``None``, it returns ``{"successful": successful}``
      as output_data.
    """
    if '_devilry_extjs' in request.GET or 'HTTP_X_DEVILRY_USE_EXTJS' in request.META:
        if isinstance(output_data, dict):
            output_data['successful'] = successful
        elif output_data == None:
            output_data = dict(successful=successful)
        return True, output_data
    return False, None
