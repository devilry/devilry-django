#!/usr/bin/env python

import os
import sys
import os.path
import logging
import textwrap
from shutil import rmtree
from subprocess import call, Popen, PIPE, STDOUT
from datetime import datetime
from optparse import OptionParser

from django.utils.importlib import import_module


class BackupError(Exception):
    pass



def callexp(cmd):
    """ Like os.system, but with good error handling. """
    logging.info("Running: %(cmd)s" % vars())
    try:
        retcode = call(cmd, shell=True)
        if retcode < 0:
            raise BackupError(
                    "'%(cmd)s' was terminated by signal -%(retcode)s" % vars())
        elif retcode > 0:
            raise BackupError(
                    "'%(cmd)s' returned error code: %(retcode)s" % vars())
    except OSError, e:
        raise BackupError(
                "Excecution of %(cmd)s failed: %(e)s" % vars())

def fsdeliverystore_backup(tarfile, filesroot):
    cmd = "tar -cvjf %(tarfile)s -C %(filesroot)s ./" % vars()
    callexp(cmd)

def fsdeliverystore_restore(tarfile, filesroot):
    cmd = "tar -xvjf %(tarfile)s -C %(filesroot)s" % vars()
    callexp(cmd)

def fsdeliverystore_clear(filesroot):
    logging.info("Removing all directories with digits as name from "\
            "%(filesroot)s" % vars())
    for dirname in os.listdir(filesroot):
        if dirname.isdigit():
            rmtree(os.path.join(filesroot, dirname))


def backup(settings, opt, backupdir, djangoadmin):
    os.makedirs(backupdir)
    logging.info("Creating backup in %(backupdir)s." % vars())

    dbdumpfile = os.path.join(backupdir, "db.json")
    fsdeliverystore_tarfile = os.path.join(backupdir, 'fsdeliverystore.tar.bz2')

    # DB backup
    f = open(dbdumpfile, 'wb')
    logging.info("Backing up the database to %(dbdumpfile)s..." % vars())
    p = Popen([djangoadmin, 'dumpdata', '--indent=4',
            '--settings', opt.settings],
        stdout=f, stderr=PIPE)
    stderr = p.communicate()[1].strip()
    f.close()
    if stderr:
        logging.warning("Error messages from db dump: %s" % stderr)
    logging.info("... database backup complete")

    # File backup
    logging.info("Backing up the files ...")
    if settings.DELIVERY_STORE_BACKEND == 'devilry.core.deliverystore.FsDeliveryStore':
        logging.info("Storing files in %(fsdeliverystore_tarfile)s." %
                vars())
        try:
            fsdeliverystore_backup(fsdeliverystore_tarfile,
                    settings.DELIVERY_STORE_ROOT)
        except BackupError, e:
            logging.error(str(e))
        logging.info("... file backup complete")
    else:
        logging.error(
                "The backup script only supports FsDeliveryStoreBackend")
        raise SystemExit()

    logging.info("*** Successful backup to: %(backupdir)s" % vars())

def restore(settings, opt, restoredir, djangoadmin):
    print
    q = textwrap.fill("We are about to to a restore of a backup. " \
            "This action will destroy all data in the database " \
            "and clear all delivered files! Are you sure you want to " \
            "continue? [yes/no]")
    inp = raw_input(q + " ")
    if inp != 'yes':
        raise SystemExit("Restore aborted")

    dbdumpfile = os.path.join(restoredir, "db.json")
    fsdeliverystore_tarfile = os.path.join(restoredir, 'fsdeliverystore.tar.bz2')

    # Clear db
    logging.info("Clearing the database")
    #if settings.DATABASE_ENGINE.startswith('postgresql'):
        #os.system("%(sql sqlreset myapp | sed 's/DROP TABLE
                #\(.*\);/DROP TABLE \1 CASCADE;/g' | psql --username
                #myusername mydbname
    for app in settings.INSTALLED_APPS:
        appname = app.split('.')[-1]
        settingsmod = opt.settings
        cmd = "%(djangoadmin)s reset --settings %(settingsmod)s --noinput %(appname)s" % vars()
        callexp(cmd)

    # DB restore
    logging.info("Restoring the database from %(dbdumpfile)s..." % vars())
    settingsmod = opt.settings
    callexp("%(djangoadmin)s loaddata --settings %(settingsmod)s " \
            "%(dbdumpfile)s" % vars())
    logging.info("... database restore complete")

    # Remove existing files
    logging.info("Removing old the delivery-files ...")

    # File restore
    logging.info("Restoring the files ...")
    if settings.DELIVERY_STORE_BACKEND == 'devilry.core.deliverystore.FsDeliveryStore':
        logging.info("Restoring delivery-files from %(fsdeliverystore_tarfile)s." %
                vars())
        try:
            fsdeliverystore_clear(settings.DELIVERY_STORE_ROOT)
            fsdeliverystore_restore(fsdeliverystore_tarfile,
                    settings.DELIVERY_STORE_ROOT)
        except BackupError, e:
            logging.error(str(e))
        logging.info("... delivery-files restore complete")
    else:
        logging.error(
                "The backup script only supports FsDeliveryStoreBackend")
        raise SystemExit()

    logging.info("*** Successful restore from: %(restoredir)s" % vars())


if __name__ == "__main__":
    p = OptionParser(
            usage = "%prog [options] <backup|restore> <backupdir> [restoredir]")
    p.add_option("--settings", dest="settings", default='devilry.settings',
            help="Django settings file.", metavar="SETTINGS")
    p.add_option("--djangoadmin-script", dest="djangoadmin",
            default='django-admin.py',
            help="Path to the django-admin.py script. Defaults to "\
                "'django-admin.py', which means that it must be on the PATH.",
                metavar="PATH")
    p.add_option("-q", "--quiet", action="store_const",
        const=logging.ERROR, dest="loglevel", default=logging.INFO,
        help="Don't show extra information (only errors).")
    p.add_option("--no-backup-on-restore", action="store_false",
        dest="backup_on_restore", default=True,
        help="Normally a backup is made before a restore (because restore "\
            "destroys data). Use this to skip the backup.")
    (opt, args) = p.parse_args()


    def exit_help():
        p.print_help()
        raise SystemExit()
    if len(args) < 2:
        exit_help()

    logging.basicConfig(level=opt.loglevel)
    try:
        settings = import_module(opt.settings)
    except ImportError, e:
        logging.error("Could not load: %s: %s" % (opt.settings, e))
        raise SystemExit()
    action = args[0]
    djangoadmin = opt.djangoadmin

    if not action in ("backup", "restore"):
        exit_help()
    if action == "backup" and len(args) != 2:
        exit_help()
    if action == "restore" and len(args) != 3:
        exit_help()

    if action == "backup" or opt.backup_on_restore:
        backupdir = os.path.join(args[1], opt.settings,
                datetime.now().isoformat())
        backup(settings, opt, backupdir, djangoadmin)

    if action == "restore":
        restoredir = args[2]
        restore(settings, opt, restoredir, djangoadmin)
