import textwrap
from os import listdir, getcwd
from os.path import dirname, abspath, join, exists
from subprocess import call, Popen, PIPE
from sys import argv, executable
from os import environ, chdir
from argparse import ArgumentParser

def getdir(filepath):
    """ Get the directory component of the given *filepath*. """
    return abspath(dirname(filepath))

def getthisdir():
    """ Get the directory containing this module (and all commands). """
    return getdir(__file__)

def get_devilryadminfixture_path(fixturename):
    """ Returns the path to a fixture within the ``fixtures/`` subdirectory of
    *this dir* (see :func:`getthisdir`).  """
    return join(getthisdir(), 'fixtures', fixturename)

def load_devilryadmin_fixture(fixturename):
    """ Load the given fixture, its path is detected using
    :func:`get_devilryadminfixture_path`. """
    fixturepath = get_devilryadminfixture_path(fixturename)
    print "Loading fixture: {0}".format(fixturepath)
    call([executable, 'manage.py', 'loaddata', '-v0', fixturepath])

def dumpfixture(fixturepath, *appnames):
    p = Popen(['python', 'manage.py', 'dumpdata', '--indent', '2'] + list(appnames),
             stdout=PIPE)
    output = p.communicate()[0]
    open(fixturepath, 'w').write(output)

def append_pythonexec_to_command(command):
   executeable_command = [executable] + command
   return executeable_command

def getcurrentcommandname():
    """ Get current command name from ``os.environ['DEVILRYADMIN_COMMANDNAME']``. """
    return environ['DEVILRYADMIN_COMMANDNAME']

def getprogname():
    """ Get the current progname (I.E.: devilryadmin.py dosomethingcool) """
    return 'devilryadmin.py {0}'.format(getcurrentcommandname())

def getreporoot():
    """ Get the absolute path to the devilry repository root. """
    return abspath(dirname(dirname(getthisdir())))

def get_docsdir():
    """ Get the absolute path to the REPOROOT/docs/ directory. """
    return join(getreporoot(), 'docs')

def get_docs_build_dir():
    """ Get the absolute path to the REPOROOT/docs/.build/ directory. """
    return join(get_docsdir(), '.build')

def get_docs_buildhtml_dir():
    """ Get the absolute path to the REPOROOT/docs/.build/html/ directory. """
    return join(get_docs_build_dir(), 'html')

def get_docs_javascriptbuild_dir():
    """ Get the absolute path to the REPOROOT/docs/.build/html/javascript/ directory. """
    return join(get_docs_buildhtml_dir(), 'javascript')

def getappsdir():
    return join(getreporoot(), 'devilry', 'apps')

def getscriptsdir():
    """ Get the ``scripts/`` directory. """
    thisdir = getthisdir()
    return join(dirname(thisdir), 'scripts')

def getcommands():
    """ Get a list of the filename of all available commmands.

    Available commands are all .py files in this dir (see :func:`getthisdir`)
    with filenames prefixed with ``cmd_``.
    """
    return [filename for filename in listdir(getdir(__file__)) \
            if filename.startswith('cmd_') and filename.endswith('.py')]

def getcommandnames():
    """ Get the name of all available commands.

    Retreived commands using :func:`getcommandnames`, and removes the
    command prefix (``cmd_``) and suffix (``.py``) before returning
    the list.
    """
    return [filename[4:-3] for filename in getcommands()]

def checkcommands(allcommands, *cmdnames):
    """ Check that each command in ``cmdnames`` is in ``allcommands``.

    :raise SystemExit: If any of the cmdnames is not in ``allcommands``.
    """
    for cmd in cmdnames:
        if not cmd in allcommands:
            raise SystemExit('{0} is not a valid command name.'.format(cmd))


def cmdname_to_filename(commandname):
    """ Return the ``commandname`` prefixed with ``cmd_`` and suffixed with ``.py``. """
    return 'cmd_{0}.py'.format(commandname)

def gethelp(commandname):
    """
    The second line of each command file should contain command help. as a # comment.

    This function returns the everything in the second line of the given command
    except for the first character. Additionally, the resulting string is strip()ed.
    """
    filename = cmdname_to_filename(commandname)
    filepath = join(getthisdir(), filename)
    f = open(filepath)
    f.readline()
    hlp = f.readline()[1:].strip()
    f.close()
    return hlp

def getcurrenthelp():
    """ Get help for current command. """
    return gethelp(getcurrentcommandname())

def execcommand(commandname):
    """ Execute the given command. """
    commandpath = join(getthisdir(), cmdname_to_filename(commandname))
    command = [commandpath] + list(argv[2:])
    environ['DEVILRYADMIN_COMMANDNAME'] = commandname
    co = command[:]
    command = append_pythonexec_to_command(co)
    call(command)


class Command(object):
    def __init__(self, commandname, *args):
        self.commandname = commandname
        self.args = args

def depends(*cmds):
    """ Execute the given commands in the given order. """
    allcommands = getcommandnames()
    checkcommands(allcommands, *[c.commandname for c in cmds])
    for cmd in cmds:
        commandpath = join(getthisdir(), cmdname_to_filename(cmd.commandname))
        command = [commandpath] + list(cmd.args)
        environ['DEVILRYADMIN_COMMANDNAME'] = cmd.commandname
        command = append_pythonexec_to_command(command)
        call(command)

def require_djangoproject():
    """ Make sure the current working directory is a django project. """
    if not exists(join(getcwd(), 'manage.py')):
        devpath = join(getreporoot(), 'devilry', 'projects', 'dev')
        warning = ("This command requires CWD to be a django project "
                   "(a directory containing manage.py). Changing "
                   "CWD to default: {devpath}").format(devpath=devpath)
        printWarning(warning)
        chdir(devpath)

def forwardable_args():
    return argv[1:]

def printWarning(warning):
    width = 80
    marker = '#'.join('=' for x in xrange(width/2))
    print '{0}\n{1}\n{0}'.format(marker, textwrap.fill(warning, width))

class DevilryAdmArgumentParser(ArgumentParser):
    """ Extends ArgumentParser and overrides ``__init__`` to set ``prog`` to
    :func:`getprogname` and description to :func:`getcurrenthelp`. """
    def __init__(self, *args, **kwargs):
        kwargs['prog'] = getprogname()
        if 'description' in kwargs:
            kwargs['description'] = kwargs['description'].format(currenthelp=getcurrenthelp())
        else:
            kwargs['description'] = getcurrenthelp()
        super(DevilryAdmArgumentParser, self).__init__(*args, **kwargs)
