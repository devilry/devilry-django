#!/usr/bin/env python

from optparse import OptionParser

from common import (setup_logging,
    add_settings_option, set_django_settings_module, add_quiet_opt,
    add_debug_opt)


p = OptionParser(
        usage = "%prog [options] <outfile>")
add_settings_option(p)
add_quiet_opt(p)
add_debug_opt(p)
(opt, args) = p.parse_args()
setup_logging(opt)

# Django must be imported after setting DJANGO_SETTINGS_MODULE
set_django_settings_module(opt)
from django.contrib.auth.models import User
from devilry.apps.core import models
from devilry.apps.core.utils.graphviz import (recursive_get_models,
        models_to_dot, Graph)

def exit_help():
    p.print_help()
    raise SystemExit()
if len(args) != 1:
    exit_help()
setup_logging(opt)

outfile = args[0]
#devilry_models = recursive_get_models(User, "^.*$")
devilry_models = recursive_get_models(User, "^(core_.*|auth_user)$")
graph = Graph(*models_to_dot(devilry_models, show_fields=True))
print graph
open(outfile, 'wb').write(str(graph))

def dctprint(o):
    print
    print o.__class__.__name__
    for k, v in o.__dict__.iteritems():
        if not k.startswith("__"):
            print "   %s: %s" % (k, v)

#meta = User._meta
#print meta.get_all_related_many_to_many_objects()
#print meta.get_all_related_objects()
#rel = meta.get_all_related_objects()[1]
#dctprint(rel)
#fk = rel.field
#dctprint(fk)
#dctprint(fk.rel)
