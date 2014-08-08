#!/usr/bin/env python
# List all TODOs in the repository (all lines containing "TODO:")

if __name__ == '__main__':
    from subprocess import Popen, PIPE
    from common import getreporoot
    from os import getcwd, chdir
    from os.path import join, relpath, abspath
    import re

    print __file__
    IGNOREPATT = (
        'devilry/static/jslibs/.+',
        'devilry/static/superadminmedia/.+',
        'devilry/devilryadmin/cmd_todolist.py'
    )

    def ignore(fn):
        for patt in IGNOREPATT:
            if re.match(patt, fn):
                return True

    reporoot = getreporoot()
    p = Popen(['git', 'grep', '-l', 'TODO:'], stdout=PIPE, cwd=reporoot)
    stdout, stderr = p.communicate()
    matchingfiles = stdout.split()

    cwd = getcwd()
    chdir(reporoot)
    absmatchinfiles = [abspath(fn) for fn in matchingfiles]
    chdir(cwd)

    for rootrelpath, path in zip(matchingfiles, absmatchinfiles):
        if ignore(rootrelpath):
            continue
        print
        print '{0}:'.format(relpath(path))
        for lineno, line in enumerate(open(join(reporoot, path))):
            line = line.strip()
            if 'TODO:' in line:
                print '  Line {0:>5}: {1}'.format(lineno, line)
