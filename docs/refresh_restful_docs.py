#!/usr/bin/env python


from os.path import exists, join, abspath, dirname
from os import mkdir
from shutil import rmtree

from devilry.restful.createdocs import RestfulDocs
from devilry.apps.administrator.restful import administrator_restful
from devilry.apps.student.restful import student_restful
from devilry.apps.examiner.restful import examiner_restful


outdir = join(abspath(dirname(__file__)), 'restfulapi')
if exists(outdir):
    rmtree(outdir)
mkdir(outdir)


for directory, restfulmanager, indextitle in (('administrator', administrator_restful, 'Administrator'),
                                              ('examiner', examiner_restful, 'Examiner'),
                                              ('student', student_restful, 'Student')):
    subdir = join(outdir, directory)
    mkdir(subdir)
    RestfulDocs().create_in_directory(subdir,
                                      indexpageref = 'restful_api{0}'.format(directory),
                                      indextitle = indextitle,
                                      restfulmanager = restfulmanager)
