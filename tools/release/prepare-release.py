#!/usr/bin/env python
"""
Ref for the argparse setup: https://mike.depalatis.net/blog/simplifying-argparse.html
"""
from argparse import ArgumentParser
import shlex
import subprocess
import sys


cli = ArgumentParser()
subparsers = cli.add_subparsers(dest="subcommand")


def subcommand(args=[], parent=subparsers):
    def decorator(func):
        parser = parent.add_parser(func.__name__, description=func.__doc__)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)
    return decorator


def argument(*name_or_flags, **kwargs):
    return ([*name_or_flags], kwargs)


@subcommand([
    argument(
        '--apply',
        help='Apply changes. If this is not provided, we only print the actions that would be performed.',
        action='store_true'
    ),
    argument(
        '--version',
        required=False,
        help='Override version'
    )
])
def prepare(args):
    """
    New release docs

    $ nvm use 14
    $ tools/release/prepare-release.py prepare --apply
    $ git push && git push --tags

    $ hatch build -t sdist
    $ hatch publish
    $ rm dist/*              # optional cleanup
    """
    apply = args.apply
    version = args.version

    cz_bump_command = ['cz', 'bump']
    if version:
        cz_bump_command.append(version)

    commands = [
        cz_bump_command,
        ['git', 'rm', '-r', 'devilry/devilry_theme3/static/devilry_theme3/'],
        ['git', 'rm', '-r', 'devilry/devilry_statistics/static/devilry_statistics/'],
        ['ievv', 'buildstatic', '--production', '--npm-clean-node-modules'],
        ['git', 'add', 'devilry/devilry_theme3/static/devilry_theme3/'],
        ['git', 'add', 'devilry/devilry_statistics/static/devilry_statistics/'],
        ['git', 'commit', '-m', 'build: staticfiles']
    ]

    for command in commands:
        if apply:
            try:
                subprocess.run(
                    command,
                    check=True,
                    text=True
                )
            except subprocess.CalledProcessError as e:
                print(e.stdout, flush=True)
                print(e.stderr, file=sys.stderr, flush=True)
        else:
            print(f'{shlex.join(command)}', flush=True)


if __name__ == '__main__':
    args = cli.parse_args()
    if args.subcommand is None:
        cli.print_help()
    else:
        args.func(args)
