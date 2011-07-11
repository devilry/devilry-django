#!/usr/bin/env python


from os.path import exists, join, abspath, dirname
from os import mkdir
from shutil import rmtree

from devilry.restful.createdocs import RestfulDocs
from devilry.apps.administrator.restful import administrator_restful


directory = join(abspath(dirname(__file__)), 'restfulapi')
if exists(directory):
    #raise SystemExit('{0} exists. Delete it before running this script.')
    rmtree(directory)
mkdir(directory)


subdir = join(directory, 'administrator')
mkdir(subdir)
RestfulDocs().create_in_directory(subdir, 'restful_apiadministrator', administrator_restful)
