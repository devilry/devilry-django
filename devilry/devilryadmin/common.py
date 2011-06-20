from os import listdir, system, getcwd
from os.path import dirname, abspath, join, exists

def getdir(filename):
    return abspath(dirname(filename))

def getthisdir():
    return getdir(__file__)

def getreporoot():
    return abspath(dirname(dirname(getthisdir())))

def getscriptsdir():
    thisdir = getthisdir()
    return join(dirname(thisdir), 'scripts')

def getcommands():
    return [fn for fn in listdir(getdir(__file__)) \
            if fn.startswith('cmd_') and fn.endswith('.py')]

def getcommandnames():
    return [fn[4:-3] for fn in getcommands()]

def checkcommands(allcommands, *cmdnames):
    for cmd in cmdnames:
        if not cmd in allcommands:
            raise SystemExit('{0} is not a valid command name.'.format(cmd))

def cmdname_to_filename(cmdname):
    return 'cmd_{0}.py'.format(cmdname)

def gethelp(cmdname):
    filename = cmdname_to_filename(cmdname)
    filepath = join(getthisdir(), filename)
    f = open(filepath)
    f.readline()
    hlp = f.readline()[1:].strip()
    f.close()
    return hlp

def execcommand(cmdname):
    system(join(getthisdir(), cmdname_to_filename(cmdname)))

def depends(*cmdnames):
    allcommands = getcommandnames()
    checkcommands(allcommands, *cmdnames)
    for cmd in cmdnames:
        execcommand(cmd)

def require_djangoproject():
    if not exists(join(getcwd(), 'manage.py')):
        raise SystemExit('This command requires CWD to be a django project (a directory containing manage.py).')
