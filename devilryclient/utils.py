from os.path import dirname, join, exists, sep
from os import listdir, environ, mkdir
from subprocess import call
import sys
import logging
import argparse
import os
#from devilryclient.restfulclient import RestfulFactory
from ConfigParser import ConfigParser

import datetime
import time


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
    filenames = listdir(join(dirname(__file__), 'plugins'))
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
    #TODO should not search for .py files
    path = join(getpluginsdir(), command + ".py")
    if exists(path):
        commands = pathwithargs(path, args)
        call(commands)
    else:
        #command not found in devilry pulgins, must be a local command in .devilry folder
        path = join(environ['HOME'], '.devilry', 'plugins', command + '.py')
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


def create_folder(path):
    """
    :param folder_name: A string representing the node attribute which the folder should be named after
    """
    if not exists(path):
        logging.debug('INFO: Creating {}'.format(path))
        mkdir(path)
    return path


def get_config():
    """Return a ConfigParser object that can be used immediately"""
    config = ConfigParser()
    config.read(join(findconffolder(), 'config'))
    return config


def get_metadata():
    """Try to fetch .devilry/metadata. Raise an exception if it
    doesn't exist"""

    conf_dir = findconffolder()

    metadata_f = open(join(conf_dir, 'metadata'), 'r')
    metadata = eval(metadata_f.read())
    metadata_f.close()
    return metadata


def save_metadata(metadata):
    conf_dir = findconffolder()
    metadata_f = open(join(conf_dir, 'metadata'), 'w')
    metadata_f.write(str(metadata))
    metadata_f.close()


# def get_metadata_from_path(path, metadata=None):
#     """Given a path, find the the context the path belongs to, and
#     the metadata for that level.

#     :return: (context, metadata)
#     """
#     root_dir = dirname(findconffolder())
#     split_path = path.replace(root_dir, '').split(sep)

#     # might be a plugin already fetched the metadata, so no need to
#     # fetch it again
#     if not metadata:
#         metadata = get_metadata()

#     # alias split_path to something shorter
#     p = split_path
#     d = len(split_path)  # d for depth

#     if d == 1:
#         return metadata
#     elif d == 2:
#         return metadata[p[1]]
#     elif d == 3:
#         return metadata[p[1]][p[2]]
#     elif d == 4:
#         return metadata[p[1]][p[2]][p[3]]
#     elif d == 5:
#         return metadata[p[1]][p[2]][p[3]][p[4]]
#     elif d == 6:
#         return metadata[p[1]][p[2]][p[3]][p[4]][p[5]]
#     elif d == 7:
#         return metadata[p[1]][p[2]][p[3]][p[4]][p[5]][p[6]]
#     else:
#         return metadata[p[1]][p[2]][p[3]][p[4]][p[5]][p[6]][p[7]]


def deadline_format(deadline):
    deadline = deadline.replace(':', '')
    deadline = deadline.replace('-', '')
    deadline = deadline.replace(' ', '-')
    deadline = deadline[:-2]
    return deadline


def deadline_unformat(deadline):
    return datetime.datetime.fromtimestamp(time.mktime(time.strptime(deadline, "%Y%m%d-%H%M")))


def is_late(delivery):
    """
    Check if delivery is delivered after the deadline
    """
    deadline_time = delivery['deadline__deadline']
    delivery_time = delivery['time_of_delivery']
    return delivery_time > deadline_time
