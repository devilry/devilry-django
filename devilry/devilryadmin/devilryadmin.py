#!/usr/bin/env python


if __name__ == '__main__':
    from os import linesep
    from sys import argv
    from common import getdir, getcommandnames, execcommand, gethelp

    thisdir = getdir(__file__)
    commandnames = getcommandnames()

    def exit_help():
        commandlist = '{linesep} - '.format(linesep=linesep).join(commandnames)
        print 'Usage: {progname} <command>'.format(progname=argv[0])
        print
        print 'Where command is one of:'
        for cmdname in commandnames:
            print ' - {0:<30} {1}'.format(cmdname, gethelp(cmdname))
        raise SystemExit()

    if len(argv) < 2:
        exit_help()
    cmdname = argv[1]

    if cmdname == "--completionlist":
        print ' '.join(commandnames)
    else:
        if not cmdname in commandnames:
            exit_help()
        execcommand(cmdname)
