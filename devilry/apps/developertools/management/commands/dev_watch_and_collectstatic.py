from os.path import abspath
import time
import logging
#from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.core import management
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from fnmatch import fnmatch


class DjangoFileSystemEventHandler(FileSystemEventHandler):
    def __init__(self, ignorepatterns):
        self.ignorepatterns = ignorepatterns
        #self.last_event_time = datetime(2000, 1, 1)
        super(DjangoFileSystemEventHandler, self).__init__()

    def on_any_event(self, event):
        #diff = datetime.now() - self.last_event_time
        #diff_sec = diff.total_seconds()
        path = event.src_path
        for ignorepatt in self.ignorepatterns:
            if(fnmatch(path, ignorepatt)):
                print('Ignored {path} because of the "{ignorepatt}" ignorepattern'.format(**vars()))
                return
        print('Change detected in: {}'.format(path))
        management.call_command('collectstatic', interactive=False)


class Command(BaseCommand):
    help = 'Watch a directory, and and run ``collectstatic`` if any changes to the directory is detected.'
    args = '<directory to watch>'
    ignorepatterns = ['.*.swp', '*~', '*.pyc']

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Takes one argument: The directory to watch.')
        path = abspath(args[0])

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        print('Listening for file events in:')
        print('  path: {}'.format(path))
        print('  ignorepatterns: {!r}'.format(self.ignorepatterns))
        event_handler = DjangoFileSystemEventHandler(self.ignorepatterns)
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(0.3)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

