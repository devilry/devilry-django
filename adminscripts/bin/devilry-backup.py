#!/usr/bin/env python

from optparse import OptionParser
import os
import sys
import os.path
from subprocess import call, Popen, PIPE, STDOUT
from datetime import datetime
import logging

from django.utils.importlib import import_module


class BackupError(Exception):
    pass



def callexp(cmd):
    """ Like os.system, but with good error handling. """
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
    cmd = "tar -cjf %(tarfile)s %(filesdir)s" % vars()
    callexp(cmd)



if __name__ == "__main__":
    p = OptionParser(
            usage = "%prog [options] <backup|restore> <backupdir>")
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
    (opt, args) = p.parse_args()

    if len(args) != 2:
        p.print_help()
        raise SystemExit()

    logging.basicConfig(level=opt.loglevel)
    try:
        settings = import_module(opt.settings)
    except ImportError, e:
        logging.error("Could not load: %s: %s" % (opt.settings, e))
        raise SystemExit()
    action = args[0]
    djangoadmin = opt.djangoadmin

    if action == "backup":
        backupdir = os.path.join(args[1], opt.settings,
                datetime.now().isoformat())
    elif action == "restore":
        backupdir = args[1]
    else:
        p.print_help()
        raise SystemExit()

    dbdumpfile = os.path.join(backupdir, "db.json")
    fsdeliverystore_tarfile = os.path.join(backupdir, 'fsdeliverystore.tar.bz2')


    if action == "backup":
        os.makedirs(backupdir)
        logging.info("Creating backup in %(backupdir)s." % vars())

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

        logging.info("Successful backup to: %(backupdir)s" % vars())

    elif action == "restore":
        inp = raw_input("This action will destroy all data in the database " \
                "and clear all delivered files! Are you sure you want to " \
                "continue? [yes/no] ")
        if inp != 'yes':
            raise SystemExit("Restore aborted")

        # Clear db
        logging.info("Clearing the database")
        for app in settings.INSTALLED_APPS:
            appname = app.split('.')[-1]
            cmd = "%(djangoadmin)s reset --noinput %(appname)s" % vars()
            logging.info("Running: %(cmd)s" % vars())
            callexp(cmd)

        # DB restore
        f = open(dbdumpfile, 'rb')
        logging.info("Restoring the database from %(dbdumpfile)s..." % vars())
        p = Popen([djangoadmin, 'loaddata', '--settings', opt.settings],
            stdout=PIPE, stderr=STDOUT, stdin=f)
        stdout = p.communicate()[0]
        f.close()
        logging.info(stdout)
        logging.info("... database restore complete")

        # File restore
        logging.info("Restoring the files ...")
        if settings.DELIVERY_STORE_BACKEND == 'devilry.core.deliverystore.FsDeliveryStore':
            logging.info("Restoring files from %(fsdeliverystore_tarfile)s." %
                    vars())
            #try:
                #fsdeliverystore_backup(fsdeliverystore_tarfile,
                        #settings.DELIVERY_STORE_ROOT)
            #except BackupError, e:
                #logging.error(str(e))
            logging.info("... file restore complete")
        else:
            logging.error(
                    "The backup script only supports FsDeliveryStoreBackend")
            raise SystemExit()

        logging.info("Successful restore from: %(backupdir)s" % vars())
