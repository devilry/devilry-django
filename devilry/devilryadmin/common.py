from os import listdir, getcwd
from os.path import dirname, abspath, join, exists
from subprocess import call
from sys import argv
from os import environ

def getdir(filename):
    return abspath(dirname(filename))

def getthisdir():
    return getdir(__file__)

def getprogname():
    return 'devilryadmin.py {0}'.format(environ['DEVILRYADMIN_COMMANDNAME'])

def getreporoot():
    return abspath(dirname(dirname(getthisdir())))

def getscriptsdir():
    thisdir = getthisdir()
    return join(dirname(thisdir), 'scripts')

def getcommands():
    return [filename for filename in listdir(getdir(__file__)) \
            if filename.startswith('cmd_') and filename.endswith('.py')]

def getcommandnames():
    return [filename[4:-3] for filename in getcommands()]

def checkcommands(allcommands, *cmdnames):
    for cmd in cmdnames:
        if not cmd in allcommands:
            raise SystemExit('{0} is not a valid command name.'.format(cmd))

def cmdname_to_filename(commandname):
    return 'cmd_{0}.py'.format(commandname)

def gethelp(commandname):
    filename = cmdname_to_filename(commandname)
    filepath = join(getthisdir(), filename)
    f = open(filepath)
    f.readline()
    hlp = f.readline()[1:].strip()
    f.close()
    return hlp

def execcommand(commandname):
    commandpath = join(getthisdir(), cmdname_to_filename(commandname))
    command = [commandpath] + list(argv[2:])
    environ['DEVILRYADMIN_COMMANDNAME'] = commandname
    call(command)

def depends(*cmdnames):
    allcommands = getcommandnames()
    checkcommands(allcommands, *cmdnames)
    for cmd in cmdnames:
        execcommand(cmd)

def require_djangoproject():
    if not exists(join(getcwd(), 'manage.py')):
        raise SystemExit('This command requires CWD to be a django project (a directory containing manage.py).')
