# vim: ft=python


def application(eviron, start_response):
    out = 'Hello world'
    start_response('200 OK', [('Content-type', 'text/plain'),
        ('Content-length', str(len(out)))])
    return [out]
