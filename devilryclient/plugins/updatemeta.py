#!/usr/bin/env python
from devilryclient.utils import findconffolder, get_config, get_metadata
from os.path import dirname, join, sep, exists
from os import listdir


class DevilryClientUpdateMeta(object):
    #traverse meta tree and make various counts and add to .meta dicts


    def __init__(self):
        self.conf = get_config()
        self.root_dir = dirname(findconffolder())
        self.metadata = get_metadata()
        #count starts at -1 to avoid counting .meta dicts
        self.num_groups = 0
        self.num_subjects = 0
        self.num_deliveries = 0
        self.num_feedbacks = 0
        #assignment_group.candidate list
        #antall deliveries i hvert nivaa
        #antall assignmentgroups i hvert nivaa
        #antall feedbacks
        #antall late deliveries

    def run(self):
        self.count_subjects(self.metadata)

    def count_subjects(self, subjects): 
        for subject in subjects.keys():
            if subject[0] != '.':
                print subject
                self.num_subjects += 1
                self.count_periods(subjects[subject])

    def count_periods(self, periods):
        for period in periods.keys():
            if period[0] != '.':
                print period
                self.count_assignments(periods[period])

    def count_assignments(self, assignments):
        for assignment in assignments.keys():
            if assignment[0] != '.':
                print assignment
                self.count_groups(assignments[assignment])

    def count_groups(self, groups):
        for group in groups.keys():
            if group[0] != '.':
                print group
                self.count_deadlines(groups[group])

    def count_deadlines(self, deadlines):
        for deadline in deadlines.keys():
            if deadline[0] != '.':
                print deadline
                self.count_deliveries(deadlines[deadline])

    def count_deliveries(self, deliveries):
        for delivery in deliveries.keys():
            if delivery[0] != '.':
                print delivery
                self.count_files(deliveries[delivery])

    def count_files(self, files):
        for f in files['files']:
            print f
            #if deadline[0] != '.':
            #    print deadline
            #    self.count_deliveries(deadlines[deadline])

                            #self.num_periods += 1
                

if __name__ == '__main__':
    DevilryClientUpdateMeta().run()
