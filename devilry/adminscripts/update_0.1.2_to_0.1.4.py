#!/usr/bin/env python

from devilry.apps.core.models import Delivery, AssignmentGroup, Deadline
from django.db import models
import sys

min_range = -1
max_range = -1



#def set_up_deliveries_on_deadlines(update_db, groups):
#    
#    print "groups:", len(groups)
#    count = 0
#
#    for ag in groups:
#        count += 1
#
#        if count < min_range:
#            continue
#
#        if count > max_range:
#            break
#        
#        print "\n%d" % count
#        
#        print "Pre condition"
#
#        deadlines = ag.deadlines.all().order_by('deadline')
#        for d in deadlines:
#            print "Deadline:", d
#
#        dels = ag.deliveries.all()
#        for d in dels:
#            print "Delivery:", d
#
#            
#        #print "\n"
#        # Create the default deadline, with deadline at the beginning of the period
#        default_d = Deadline()
#        default_d.deadline = ag.parentnode.parentnode.start_time
#        default_d.assignment_group = ag
#        default_d.is_head = True
#       
#        deadlines = ag.deadlines.all().order_by('deadline')
#
#        # If script is run multiple times, avoid adding a new head deadline
#        if len(deadlines) == 0 or deadlines[0].is_head:
#            print "Created new head deadline with time %s", default_d.deadline
#
#            if update_db:
#                default_d.save()
#
#        for d in ag.deliveries.all():
#            # Find correct deadline and tag the delivery 
#            last_deadline = None
#            for tmp_d in deadlines:
#                last_deadline = tmp_d
#                if d.time_of_delivery < tmp_d.deadline:
#                    d.deadline_tag = tmp_d
#                    print "Tag2"
#                    # Found deadline, so break
#                    break
#            # Delivered too late, so use the last deadline
#            if d.deadline_tag == None and not last_deadline == None:
#                d.deadline_tag = last_deadline
#                print "Tag2:%s --- (%s)" % (d, d.deadline_tag)
#
#            if update_db:
#                print "save deadline"
#                d.save()
#
#        d2 = ag.deadlines.all().order_by('-deadline')
#
#        #ag._update_status
#        #if not ag.is_open:
#        #    ag.status = AssignmentGroup.CORRECTED_AND_CLOSED
#        #    ag.save()
#        #    print "Setting group to CORRECTED_AND_CLOSED"
#        #else:
#            
#
#        if len(d2) < 2 or True:
#            print "\nPeriod:    ", ag.parentnode.parentnode.start_time
#            print "Assignment: %s (%d)" % (ag, ag.id)
#            print "deadline count:", len(d2)
#            for deadline in d2:
#                print "  Deadline:", deadline
#                for delivery in deadline.deliveries.all():
#                    print "          - %s (Late:%s)" % (delivery.time_of_delivery, delivery.after_deadline)
#
#        
#        update_status(ag, update_db)
#        print "Status:", AssignmentGroup.status_mapping[ag.status]
#
#        #if count == 2000:
#        #    break
#


def update_status(ag, update_db):
    deadlines = ag.deadlines.all().order_by('deadline')
    for d in deadlines:
        print "Deadline:", d

def create_default_deadline(update_db, ag):
    # Create the default deadline, with deadline at the beginning of the period
    default_d = Deadline()
    default_d.deadline = ag.parentnode.parentnode.start_time
    default_d.assignment_group = ag
    default_d.is_head = True
    
    deadlines = ag.deadlines.all().order_by('deadline')
    # If script is run multiple times, avoid adding a new head deadline
    if len(deadlines) == 0 or deadlines[0].is_head:
        print "Created new head deadline with time %s", default_d.deadline
        if update_db:
            default_d.save()

def tag_deliveries_with_deadline(update_db, ag):
    deadlines = ag.deadlines.all().order_by('deadline')
    for d in ag.deliveries.all():
        # Find correct deadline and tag the delivery 
        last_deadline = None
        for tmp_d in deadlines:
            last_deadline = tmp_d
            if d.time_of_delivery < tmp_d.deadline:
                d.deadline_tag = tmp_d
                print "Tag2"
                # Found deadline, so break
                break
        # Delivered too late, so use the last deadline
        if d.deadline_tag == None and not last_deadline == None:
            d.deadline_tag = last_deadline
            print "Tag2:%s --- (%s)" % (d, d.deadline_tag)

        if update_db:
            print "save deadline"
            d.save()

def debug_print(count, ag):
    print "\n%d" % count
    print "Pre condition"
    deadlines = ag.deadlines.all().order_by('deadline')
    for d in deadlines:
        print "Deadline:", d
    dels = ag.deliveries.all()
    for d in dels:
        print "Delivery:", d

def set_up_deliveries_on_deadlines(update_db, groups):
    
    print "groups:", len(groups)
    count = 0

    for ag in groups:
        count += 1
        if min_range > -1 and count < min_range:
            continue
        if max_range > -1 and count > max_range:
            break
        
        debug_print(count, ag)
        
        create_default_deadline(update_db, ag)
        tag_deliveries_with_deadline(update_db, ag)
        
        d2 = ag.deadlines.all().order_by('-deadline')

        #ag._update_status
        #if not ag.is_open:
        #    ag.status = AssignmentGroup.CORRECTED_AND_CLOSED
        #    ag.save()
        #    print "Setting group to CORRECTED_AND_CLOSED"
        #else:
            

        if len(d2) < 2 or True:
            print "\nPeriod:    ", ag.parentnode.parentnode.start_time
            print "Assignment: %s (%d)" % (ag, ag.id)
            print "deadline count:", len(d2)
            for deadline in d2:
                print "  Deadline:", deadline
                for delivery in deadline.deliveries.all():
                    print "          - %s (Late:%s)" % (delivery.time_of_delivery, delivery.after_deadline)

        
        update_status(ag, update_db)
        print "Status:", AssignmentGroup.status_mapping[ag.status]
   

if __name__ == "__main__":
    update_db = True
    if len(sys.argv) == 2:
        if sys.argv[1] == "test":
            update_db = False
    print "Update database:", update_db
    
    groups = AssignmentGroup.objects.all()
    #groups = AssignmentGroup.objects.filter(pk=8161)
    #groups = AssignmentGroup.objects.filter(pk=8308)

    set_up_deliveries_on_deadlines(update_db, groups)
