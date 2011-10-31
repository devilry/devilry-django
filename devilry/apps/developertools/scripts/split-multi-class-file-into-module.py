#!/usr/bin/env python

import sys
import re
import shutil
from os.path import join, splitext, exists
from os import mkdir

DEFSFILENAME = 'helpers.py'
CLSPATTSTR = '(?:\n@.+?)?\nclass '
DEFPATTSTR = '(?:\n@.+?)?\ndef '
FINDCLASSESPATT = re.compile('({CLSPATTSTR}.*?)(?:(?=(?:{CLSPATTSTR})|(?:{DEFPATTSTR})|$))'.format(**globals()), re.DOTALL)
FINDDEFPATT = re.compile('({DEFPATTSTR}.*?)(?:(?=(?:{DEFPATTSTR})|(?:{CLSPATTSTR})|$))'.format(**globals()), re.DOTALL)
ALL_LIST_PATT = re.compile('(__all__ = \(.*?\))', re.DOTALL)


def get_classfiles_by_classname(filecontent):
    clsnamepatt = re.compile('^(?:{CLSPATTSTR})(?P<classname>\w+)'.format(**globals()))
    classes = {}
    matches = FINDCLASSESPATT.findall(filecontent)
    for classstr in matches:
        classname = clsnamepatt.match(classstr).groupdict()['classname']
        classes[classname] = classstr.strip()
    return classes


def get_defs(filecontent):
    return FINDDEFPATT.findall(filecontent)

def create_defs_file(moduledir, header, filecontent):
    defs = '\n\n\n'.join([x.strip() for x in get_defs(filecontent)])
    open(join(moduledir, DEFSFILENAME), 'w').write('{header}\n\n\n\n{defs}'.format(**vars()))

def create_moduledir(moduledir):
    if exists(moduledir):
        #raise SystemExit('{0} exists. Please delete it and re-run the script.'.format(moduledir))
        shutil.rmtree(moduledir)
    mkdir(moduledir)

def create_init(moduledir, classnames):
    imports = '\n'.join(['from {0} import {1}'.format(classname.lower(), classname) for classname in classnames])
    all_list = ', '.join(["'{0}'".format(classname) for classname in classnames])
    open(join(moduledir, '__init__.py'), 'w').write('{imports}\n\n__all__ = ({all_list})'.format(**vars()))

def create_classfiles(moduledir, classes, header):
    for classname, classstr in classes.iteritems():
        filename = classname.lower() + '.py'
        open(join(moduledir, filename), 'w').write('{header}\n\n\n{classstr}'.format(**vars()))

def get_header(filecontent):
    header = FINDCLASSESPATT.sub('', filecontent)
    header = FINDDEFPATT.sub('', header)
    header = ALL_LIST_PATT.sub('', header)
    return header.strip()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: {0} <filename>'.format(sys.argv[0]))

    filename = sys.argv[1]
    moduledir = splitext(filename)[0]
    filecontent = open(filename).read()

    header = get_header(filecontent)
    classes = get_classfiles_by_classname(filecontent)
    create_moduledir(moduledir)
    create_init(moduledir, classes.keys())
    create_classfiles(moduledir, classes, header)
    create_defs_file(moduledir, header, filecontent)
