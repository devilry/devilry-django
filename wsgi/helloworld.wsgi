# vim: ft=python


def application(environ, start_response):
    out = ['Hello world']
    if environ['mod_wsgi.process_group']:
        out.append('running in process mode')
    else:
        out.append('running in embedded mode')

    #out.append('REMOTE_USER: %s' % 
            #environ.get('REMOTE_USER', "Not logged in"))

    for key, value in environ.iteritems():
        out.append('%s: %s' % (key, value))

    output = '\n'.join(out)
    start_response('200 OK', [('Content-type', 'text/plain'),
        ('Content-length', str(len(output))),
        ])
    return output
