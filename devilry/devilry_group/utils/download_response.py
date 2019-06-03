# Django imports.
from wsgiref.util import FileWrapper

# Django imports.
from django import http


def __get_bulk_size(bulk_size=None):
    """
    Get the size of chunks data should be loaded in.

    Args:
        bulk_size: Custom bulksize

    Returns:
        int: ``bulk_size`` or :class:`wsgiref.util.FileWrapper` default of 8192.
    """
    if bulk_size is None:
        return FileWrapper(None).blksize
    return bulk_size


def download_response(content_path, content_name, content_type, content_size, streaming_response=False, bulk_size=None):
    """
    Wrap data in a :obj:`wsgiref.util.FileWrapper` that returns chunks to a streamed response using
    :class:`~django.http.StreamingHttpResponse` if ``streaming_response`` is set to ``True``, else a regular
    :class:`~django.http.HttpResponse` is sent.

    Args:
        content_path: Full path to content.
        content_name: Name of content.
        content_type: Type of content, mimyetype.
        content_size: Size of content in bytes.
        streaming_response: If the response should be StreamingHttpResponse or regular HttpResponse.
        bulk_size: Byte sized chunks to be streamed.

    Returns:
        http response: :class:`~django.http.StreamingResponse` or :class:`~django.http.HttpResponse`.
    """
    content = open(content_path, 'rb')
    filewrapper = FileWrapper(content, blksize=__get_bulk_size(bulk_size))

    # Create response
    if streaming_response:
        response = http.StreamingHttpResponse(filewrapper, content_type=content_type)
    else:
        response = http.HttpResponse(filewrapper, content_type=content_type)
    response['content-disposition'] = 'attachment; filename={}'.format(
        content_name.encode('ascii', 'replace').decode()
    )
    response['content-length'] = content_size

    return response
