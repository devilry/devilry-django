from os.path import dirname, join, exists
from os import listdir, environ, mkdir
from subprocess import call
import sys, logging, argparse, os
from devilryclient.restfulclient import RestfulFactory

def helloworld():
    print "Hello world"

def showhelp():
    """
    Print the help menu
    """
    commands = getcommandlist()
    print 'Usage: {progname} <command>'.format(progname=sys.argv[0])
    print 'Commands:'
    for cmd in commands:
        print '     {}'.format(cmd[:-3]),
        print '     {}'.format(getcmdinfo(cmd))

def getcmdinfo(cmd):
    """
    :param cmd: Command (with .py ending)
    :return: Available info on cmd
    """
    path = join(getpluginsdir(), cmd)
    return "bla bla"

def getcommandlist():
    """
    :return: All available commands
    """
    filenames = listdir(join(dirname(__file__),'plugins'))
    commands = [filename for filename in filenames if filename.endswith('.py')]
    return commands

def getthisdir():
    """
    :return: Current directory
    """
    return dirname(__file__)

def getpluginsdir():
    """
    :return: Plugins directory
    """
    return join(getthisdir(), "plugins")

def pathwithargs(path, args):
    """
    Append args to path as a list

    :param path: Path of file to be called
    :param args: Namespace object of additional arguments
    :return: Path and args as a list of strings
    """
    commands = [path]
    for arg in args:
        commands.append(arg)
    return commands
   
def execute(command, args):
    """
    Execute command by calling the corresponding py-file with args as arguments

    :param command: The command to be called
    :param args: Additional arguments
    """
    logging.warning('Hello from utils.py')
    path = join(getpluginsdir(), command + ".py")
    if exists(path):
        commands = pathwithargs(path, args)
        call(commands)
    else:
        #command not found in devilry pulgins, must be a local command in .devilry folder
        path = join(environ['HOME'], '.devilry', 'plugins', command+'.py')
        if exists(path):
            commands = pathwithargs(path, args)
            call(commands)
        else:
            showhelp()
            raise SystemExit()

def logging_startup(args):
    """
    Parse the arguments in args and atart logging based on these arguments.

    Raises: SystemExit if arguments cannot be parsed

    :param args: The logging arguments
    :return: other command-specific arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', action='store_true', default=False, help='Quiet mode')
    parser.add_argument('-v', action='store_true', default=False, help='Verbose mode')
    parser.add_argument('otherargs', nargs='*', help='Additional arguments')
    try:
        args = parser.parse_args(args)
    except:
        showhelp()
        raise SystemExit()

    log_level = logging.INFO
    if args.q:
        log_level = logging.WARNING
    elif args.v:
        log_level = logging.DEBUG
    logging.basicConfig(format='%(message)s', level=log_level)
    #retrun args that are needed for command
    return args.otherargs

def findconffolder():
    """
    :return: The path of the .devilry folder containing config-file
    """
    cwd = os.getcwd()
    while cwd != environ["HOME"]:  
        if exists(join(cwd, '.devilry')):
            return join(cwd, '.devilry')
        else:
            cwd = dirname(cwd)

    raise ValueError(".devirly not found")

#TODO
def restful_setup():
    restful_factory = RestfulFactory("http://localhost:8000/")
    SimplifiedNode = restful_factory.make("administrator/restfulsimplifiednode/")
    SimplifiedSubject = restful_factory.make("administrator/restfulsimplifiedsubject/")
    SimplifiedPeriod = restful_factory.make("administrator/restfulsimplifiedperiod/")
    SimplifiedAssignment = restful_factory.make("administrator/restfulsimplifiedassignment/")
    return [SimplifiedNode, SimplifiedSubject, SimplifiedPeriod, SimplifiedAssignment]


#TODO
def create_folder(node, parent_path, folder_name):
    """
    :param folder_name: A string representing the node attribute which the folder should be named after
    """
    path = join(parent_path, str(node[folder_name]))
    if not exists(path):
        logging.debug('INFO: Creating {}'.format(path))
        mkdir(path)
    return path
     
