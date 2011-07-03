#!/usr/bin/env python
# Generate javascript docs in REPOROOT/docs/javascript/.
"""
Requires JSDuck: https://github.com/nene/jsduck
"""
from subprocess import call
import SimpleHTTPServer
import SocketServer
from os import chdir, walk, makedirs
from os.path import exists
from shutil import rmtree

from common import getappsdir


def find_javascriptfiles():
    jsfiles = []
    for root, dirs, files in walk(getappsdir()):
        is_devilry_doc = 'extjs_classes' in root
        if is_devilry_doc:
            for filename in files:
                if filename.endswith('.js'):
                    filepath = join(root, filename)
                    jsfiles.append(filepath)
    return jsfiles

def build(outdir):
    infiles = find_javascriptfiles()
    retcode = call(['jsduck', '--verbose', '--output', outdir] + infiles)
    if not exists(outdir):
        makedirs(outdir)

    print
    if retcode == 0:
        print "Docs build successfully in:"
        print outdir
        print "Use --serve to browse the docs."
    else:
        print "JSDuck exited with error code {}.".format(retcode)


def serve(outdir):
    chdir(outdir)
    addr = ("localhost", 9191)
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    class CustTCPServer(SocketServer.TCPServer):
        allow_reuse_address = True
    httpd = CustTCPServer(addr, Handler)

    print
    print "Serving docs at port http://{0}:{1}".format(*addr)
    httpd.serve_forever()

def clean(outdir):
    if exists(outdir):
        print "Removing", outdir
        rmtree(outdir)
    else:
        print "Not cleaning", outdir, "because it does not exist."

if __name__ == '__main__':
    from os.path import join
    from sys import exit

    from common import (get_docs_javascriptbuild_dir, DevilryAdmArgumentParser,
                        getprogname)

    epilog = 'Example: {prog} --clean --build --serve'.format(prog=getprogname())
    parser = DevilryAdmArgumentParser(description='Process some integers.',
                                      epilog=epilog)
    parser.add_argument('-b', '--build', action='store_true',
                       help='Build javascript docs.')
    parser.add_argument('-s', '--serve', action='store_true',
                       help='Serve generated javascript docs on http://localhost:9191')
    parser.add_argument('-c', '--clean', action='store_true',
                       help='Remove the generated javascript docs.')
    parser.add_argument('--completionlist', action='store_true',
                       help='Print completionlist for bash completion.')
    args = parser.parse_args()
    if args.completionlist:
        print "--build --serve --clean"
        exit(0)
    if not (args.build or args.serve or args.clean):
        parser.print_help()
        print
        parser.error('--build, --serve or --clean must be supplied.')


    outdir = get_docs_javascriptbuild_dir()

    if args.clean:
        clean(outdir)
    if args.build:
        build(outdir)
    if args.serve:
        serve(outdir)
