#!/usr/bin/env python

from os import system


ro = ('tworide', 'rebekkjm', 'vegarang', 'espenak', 'bendikro', 'klfd4', 'devilry')
repos = ['{0}-ro'.format(name) for name in ro]

print "*** Removing remotes. Will show an error for each remote that is not already present."
for name in ro:
    system('git remote rm {0}-ro'.format(name))
system('git remote rm devilry-rw'.format(name))

print "*** Adding remotes"
system('git remote add devilry-rw git@github.com:devilry/devilry-django.git')
for name in ro:
    system('git remote add {name}-ro https://github.com/{name}/devilry-django.git'.format(name=name))

print "*** Finished. git remote -v:"
system('git remote -v')
