from os.path import dirname, join, exists
from os import listdir, environ
from subprocess import call
import sys

def helloworld():
    print "Hello world"

def showhelp():
    commands = getcommandlist()
    print 'Usage: {progname} <command>'.format(progname=sys.argv[0])
    print 'Commands:'
    for cmd in commands:
        print '     {}'.format(cmd[:-3]),
        print '     {}'.format(getcmdinfo(cmd))

def getcmdinfo(cmd):
    return "bla bla"

def getcommandlist():
    filenames = listdir(join(dirname(__file__),'plugins'))
    commands = [filename for filename in filenames if filename.endswith('.py')]
    return commands

def getthisdir():
    return dirname(__file__)

def getpluginsdir():
    return join(getthisdir(), "plugins")


def execute(command):
    path = join(getpluginsdir(), command + ".py")
    if exists(path):
        call(path)
    else:
        #Local command
        path = join(environ['HOME'], '.devilry', 'plugins', command+'.py')
        if exists(path):
            call(path)
