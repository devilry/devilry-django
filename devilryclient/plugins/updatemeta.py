#!/usr/bin/env python
from devilryclient.utils import get_config, get_metadata, deadline_unformat, save_metadata
from os.path import dirname, sep, basename


class DevilryClientUpdateMeta(object):
    """
    Traverse meta tree and make various counts and add to .meta dicts
    .meta info is stored in the same level as the corresponding nodes. So metadata[subject]['.meta']
    holds the counters for a given subject
    """

    def __init__(self):
        self.conf = get_config()
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
            6: self.delivery_meta
            }

        # sort the keys
        for key in sorted(self.metadata.keys()):
            if key == '.meta':
                continue
            print key
            methods[self.depth(key)](key)

        save_metadata(self.metadata)

    def subject_meta(self, path):
        # alias to something shorter
        meta = self.metadata[path]['.meta']
        try:
            meta['num_subjects'] += 1
        except KeyError:
            meta['num_subjects'] = 0
        meta['num_deliveries'] = 0
        meta['num_late_deliveries'] = 0
        meta['num_periods'] = 0
        meta['num_corrected'] = 0
        meta['num_groups'] = 0
        meta['num_assignments'] = 0

    def period_meta(self, path):
        # alias to something shorter
        meta = self.metadata[path]['.meta']
        meta['num_groups'] = 0
        meta['num_deliveries'] = 0
        meta['num_late_deliveries'] = 0
        meta['num_assignments'] = 0

    def assignment_meta(self, path):
        meta = self.metadata[path]['.meta']
        meta['num_groups'] = 0
        meta['num_deliveries'] = 0
        meta['num_late_deliveries'] = 0

        # update upwards
        while dirname(path) != '':
            path = dirname(path)
            self.metadata[path]['.meta']['num_assignments'] += 1

    def group_meta(self, path):
        # alias to something shorter
        meta = self.metadata[path]['.meta']
        meta['num_deliveries'] = 0
        meta['num_late_deliveries'] = 0

        # update upwards
        while dirname(path) != '':
            path = dirname(path)
            self.metadata[path]['.meta']['num_groups'] += 1

    def deadline_meta(self, path):
        self.metadata[path]['.meta']['deadline'] = deadline_unformat(basename(path)[2:])

    def delivery_meta(self, path):
        # alias to something short
        meta = self.metadata[path]['.meta']
        meta['done'] = "TODO: noooo, we shouldnt overwrite this variable if it existed before sync"
        meta['delivery_time'] = -1
        meta['is_late'] = self.metadata[dirname(path)] < meta['delivery_time']  # is_late(self.metadata[dirname(path)]['deadline'])
        meta['delivered_by'] = 'FixMe'

        # update upwards (TODO: should only be done for the latest delivery!)

        # skip deadline, it doesn't hold num_deliveries
        path = dirname(path)
        while dirname(path) != '':
            path = dirname(path)
            self.metadata[path]['.meta']['num_deliveries'] += 1

    def file_meta(self, path_dict):
        subject = path_dict['subject']
        period = path_dict['period']
        assignment = path_dict['assignment']
        group = path_dict['group']
        deadline = path_dict['deadline']
        delivery = path_dict['delivery']
        files = self.metadata[subject][period][assignment][group][deadline][delivery]
        for f in files['files']:
            print f
            print path_dict
        print self.metadata
            #if deadline[0] != '.':
            #    print deadline
            #    self.count_deliveries(deadlines[deadline])

                            #self.num_periods += 1


if __name__ == '__main__':
    DevilryClientUpdateMeta().run()
