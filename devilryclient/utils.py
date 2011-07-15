from os.path import dirname, join, exists
from os import listdir, environ, mkdir
from subprocess import call
import sys, logging, argparse, os
import stat
from devilryclient.restfulclient import RestfulFactory
from getpass import getpass

import httplib
import urllib
from Cookie import SimpleCookie
from urlparse import urlparse
import ConfigParser


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


class Session(object):

    class LoginError(Exception):
        """Raised on login error"""

    def get_session_cookie(self):
        if exists(join(findconffolder(), 'session')):
            session = open(join(findconffolder(), 'session'), 'r')
            cookieout = session.read()
            session.close()
            return cookieout
        else:
            return self.login()

    def login(self):

        confdir = findconffolder()
        conf = ConfigParser.ConfigParser()
        conf.read(join(confdir, 'config'))

        # make the url and credentials
        url = join(conf.get('URL', 'url'), 'authenticate/login')

        username = raw_input("Username: ")
        password = getpass("Password: ")

        creds = urllib.urlencode({'username': username, 'password': password})

        parsed_url = urlparse(url)
        host = parsed_url.netloc

        if parsed_url.scheme == "https":
            conn = httplib.HTTPSConnection(host)
        else:
            conn = httplib.HTTPConnection(host)

        response = conn.request('POST', parsed_url.path, creds, {'Content-type': "application/x-www-form-urlencoded"})

        response = conn.getresponse()
        if response.status > 400:
            raise self.LoginError("Login to %s failed with the following message: %s %s (%s)" % (
                    url, response.status, response.reason, response.msg))

        response.read()
        setcookie = response.getheader('Set-Cookie')
        if setcookie == None:
            raise self.LoginError("Login failed. This is usually because of "
                             "invalid username/password, but might be "
                             "caused by wrong login urlprefix or server errors. "
                             "Technical error message: Login urlprefix did not "
                             "respond with any authorization cookies.")

        cookie = SimpleCookie()
        cookie.load(setcookie)
        cookieout = cookie.output().replace('Set-Cookie: ', '')
        session = open(join(confdir, 'session'), 'w')
        session.write(cookieout)
        session.close()

        os.chmod(join(confdir, 'session'), stat.S_IRUSR | stat.S_IWUSR)

        return cookieout
