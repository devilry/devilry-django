#!/usr/bin/env python

from optparse import OptionParser
import logging

from common import (setup_logging, load_devilry_plugins,
    add_settings_option, set_django_settings_module, add_quiet_opt,
    add_debug_opt)


p = OptionParser(
        usage = "%prog [options] <action>")
add_settings_option(p)
add_quiet_opt(p)
add_debug_opt(p)
(opt, args) = p.parse_args()
setup_logging(opt)

# Django must be imported after setting DJANGO_SETTINGS_MODULE
set_django_settings_module(opt)
load_devilry_plugins()
from devilry.adminscripts.dbsanity import dbsanity_registry

def exit_help():
    p.print_help()
    raise SystemExit()
if len(args) != 1:
    exit_help()
setup_logging(opt)

action = args[0]


if action == 'check':
    autofixable_errors = False
    for key, check in dbsanity_registry.iterchecks():
        if check.is_ok():
            logging.debug("%s: OK" % (check.get_label()))
        else:
            logging.warning("%s: CHECK FAILED" % (check.get_label()))
            if check.autofixable_errors:
                autofixable_errors = True
                logging.info("Errors that can be automatically fixed:")
                for error in check.autofixable_errors:
                    logging.info(error)
            if check.fatal_errors:
                logging.info("Errors which can not be fixed automatically:")
                for error in check.fatal_errors:
                    logging.info(error)
    if autofixable_errors:
        print
        print "There are errors that can be fixed automatically. Run "\
            "'autofix' to fix the errors."
elif action == 'fix':
    autofixable_errors = False
    for key, checkcls in dbsanity_registry.iterfix():
        logging.debug("%s: FIXED" % (checkcls.get_label()))
else:
    exit_help()
