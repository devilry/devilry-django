#!/usr/bin/env python
from devilryclient.utils import get_config, get_metadata, deadline_unformat, save_metadata, findconffolder
from os.path import dirname, sep, basename, join

from datetime import datetime


class DevilryClientUpdateMeta(object):
    """
    Traverse meta tree and make various counts and add to .meta dicts
    .meta info is stored in the same level as the corresponding nodes. So metadata[subject]
    holds the counters for a given subject
    """

    def __init__(self):
        self.conf = get_config()
        self.confdir = findconffolder()
        self.metadata = get_metadata()

    def depth(self, path):
        return len(path.split(sep))

    def run(self):

        methods = {
            1: self.subject_meta,
            2: self.period_meta,
            3: self.assignment_meta,
            4: self.group_meta,
            5: self.deadline_meta,
            6: self.delivery_meta,
            7: self.file_meta,
            }

        # initialize top-level statistics
        self.metadata[''] = {}
        self.metadata['']['num_deliveries'] = 0
        self.metadata['']['total_deliveries'] = 0
        self.metadata['']['num_late_deliveries'] = 0
        self.metadata['']['num_corrected'] = 0
        self.metadata['']['num_groups'] = 0
        self.metadata['']['num_assignments'] = 0

        # sort the keys
        for key in sorted(self.metadata.keys()):
            if key == '':
                continue
            method = methods.get(self.depth(key), None)
            if method:
                method(key)

        save_metadata(self.metadata)

    def subject_meta(self, path):
        # alias to something shorter
        meta = self.metadata[path]

        meta['num_deliveries'] = 0
        meta['num_late_deliveries'] = 0
        meta['num_corrected'] = 0
        meta['num_groups'] = 0
        meta['num_assignments'] = 0
        meta['num_corrected'] = 0

    def period_meta(self, path):
        # alias to something shorter
        meta = self.metadata[path]
        meta['num_groups'] = 0
        meta['num_deliveries'] = 0
        meta['num_late_deliveries'] = 0
        meta['num_assignments'] = 0
        meta['num_corrected'] = 0

    def assignment_meta(self, path):
        meta = self.metadata[path]
        meta['num_groups'] = 0
        meta['num_deliveries'] = 0
        meta['num_late_deliveries'] = 0
        meta['num_corrected'] = 0

        # update upwards
        while path != '':
            path = dirname(path)
            self.metadata[path]['num_assignments'] += 1

    def group_meta(self, path):
        # alias to something shorter
        meta = self.metadata[path]
        meta['num_deliveries'] = 0
        meta['num_late_deliveries'] = 0
        meta['latest_corrected'] = False

        # update upwards
        while path != '':
            path = dirname(path)
            self.metadata[path]['num_groups'] += 1

    def deadline_meta(self, path):
        self.metadata[path]['deadline'] = deadline_unformat(basename(path)[2:])
        self.metadata[path]['latest_deadline'] = False

    def delivery_meta(self, path):
        # alias to something short
        meta = self.metadata[path]

        # check if old_metadata exists, and grab the done status
        try:
            old_meta = eval(open(join(self.confdir, 'old_metadata'), 'r').read())
            meta['corrected'] = old_meta[path]['corrected']
        except Exception:
            meta['corrected'] = False

        meta['is_latest'] = False
        meta['time_of_delivery'] = datetime.strptime(meta['query_result']['time_of_delivery'], "%Y-%m-%d %H:%M:%S")
        meta['is_late'] = self.metadata[dirname(path)]['deadline'] < meta['time_of_delivery']
        meta['delivered_by'] = meta['query_result']['delivered_by__identifier']
        meta['candidates'] = meta['query_result']['deadline__assignment_group__candidates__identifier']

        # skip deadline, it doesn't hold num_deliveries
        path = dirname(path)

        # and we only want to count the latest delivery, no matter how
        # many a group has delivered
        if self.metadata[dirname(path)]['num_deliveries'] == 1:
            return

        while path != '':
            path = dirname(path)
            self.metadata[path]['num_deliveries'] += 1

    def file_meta(self, path):
        # might create some metadata for this too, some time
        pass

if __name__ == '__main__':
    DevilryClientUpdateMeta().run()
