#!/usr/bin/env python
"""
This file demonstrates the streamable archives
"""

from datetime import datetime, timedelta
from tempfile import mkdtemp
from shutil import rmtree
from os.path import join

from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from devilry.addons.grade_approved.models import ApprovedGrade

from devilry.core.models import (Node, Subject, Period, Assignment, AssignmentGroup,
        Delivery, Candidate, Feedback, FileMeta)

from devilry.core.utils.delivery_collection import create_archive_from_assignmentgroups
from devilry.core.utils.stream_archives import  MemoryIO 
from StringIO import StringIO

def stringIOTest(io):
    tmp = ''
    print "Initalized empty"
    print "tell1:%d" % io.tell()
    print "seek(0):", io.seek(0)

    tmp = str("1Test1")
    io.write(tmp)
    print "write:", tmp
    print "tell2:%d" % io.tell()

    tmp = str("2Test2")
    io.write(tmp)
    print "write:", tmp
    print "tell3:%d" % io.tell()

    ret = io.read()
    if (ret != 0):
        print "read(%d):%s" % (len(ret), ret)
    print "tell4:%d" % io.tell()

    tmp = str("3Test3")
    io.write(tmp)
    print "write:", tmp
    print "tell4:%d" % io.tell()

    ret = io.read()
    if (ret != 0):
        print "read(%d):%s" % (len(ret), ret)
    print "tell5:%d" % io.tell()

    print "seek(0):", io.seek(0)

    ret = io.read()

    if (ret != 0):
        print "read(%d):%s" % (len(ret), ret)
    print "tell6:%d" % io.tell()


import sys

if __name__ == '__main__':

    if len(sys.argv) == 2 and sys.argv[1] == "test":
        print "StringIO TEST"
        stringIOTest(StringIO())
        print "\nDevilryIO TEST"
        stringIOTest(MemoryIO())
        sys.exit()

    archive_type = "zip" 
    filename = "test." + archive_type

    if len(sys.argv) == 2 and sys.argv[1] == "all":
        ass_groups_all = []
        assignments = Assignment.objects.all()
        for assignment in assignments:
            for assignmentgroup in assignment.assignmentgroups.all():
                #assignmentgroups = assignment.assignmentgroups.all()
                ass_groups_all.append(assignmentgroup)


        assignmentgroups = ass_groups_all
    else:
        assignment = Assignment.objects.get(id=48)
        assignmentgroups = []
        assignmentgroups.append(AssignmentGroup.objects.get(id=8091))
        assignmentgroups.append(AssignmentGroup.objects.get(id=8095))
        assignmentgroups.append(AssignmentGroup.objects.get(id=8121))
        assignmentgroups.append(AssignmentGroup.objects.get(id=8145))

        assignmentgroups = assignment.assignmentgroups.all()
    
    iterator = create_archive_from_assignmentgroups(None, assignment, assignmentgroups,
                                                        archive_type)
    f = open(filename, "w")
    for bytes in iterator:
        f.write(bytes)
    f.close
        
    print "Wrote to %s" % filename
