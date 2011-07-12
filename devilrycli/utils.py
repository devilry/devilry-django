from os.path import dirname, join, exists
from os import listdir, environ
from subprocess import call, Popen
import sys, logging, argparse

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


def execute(command, args):
    #TODO need too pass args onto call(path) for logging
    logging.warning('Hello from utils.py')
    path = join(getpluginsdir(), command + ".py")
    if exists(path):
        #call(path + arg for arg in args)
        call(path)
    else:
        #command not found in devilry pulgins, must be a local command in .devilry folder
        path = join(environ['HOME'], '.devilry', 'plugins', command+'.py')
        if exists(path):
            call(path)

def logging_startup(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', action='store_true', default=False, help='Quiet mode')
    parser.add_argument('-v', action='store_true', default=False, help='Verbose mode')
    try:
       args = parser.parse_args(args)
       print "args: ", args
    except:
        showhelp()
        raise SystemExit()

    log_level = logging.INFO
    if args.q:
        log_level = logging.WARNING
    elif args.v:
        log_level = logging.DEBUG
    logging.basicConfig(format='%(message)s', level=log_level)

