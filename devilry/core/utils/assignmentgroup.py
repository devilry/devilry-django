class GroupDeliveriesByDeadline():
    def __init__(self, group):
        self.after_last_deadline = []
        self.within_a_deadline = []
        self.ungrouped_deliveries = []
        deadlines = group.deadlines.all().order_by('deadline')
        numdeadlines = len(deadlines)

        print "numdeadlines:", numdeadlines

        for d in group.deliveries.all():
            print "D:", d.deadline_tag
        
        if numdeadlines > 0:
            deliveries = group.deliveries.filter(
                    deadline_tag = None)

            #print "Deliveries:", group.deliveries.all()

            self.ungrouped_deliveries = deliveries

            # Within a deadline
            #self.within_a_deadline.append((deadlines[0], deliveries))
            previous = deadlines[0].deadline
            for d in deadlines[:]:
                deliveries = group.deliveries.filter(
                        deadline_tag = d).order_by(
                                "-time_of_delivery")
                self.within_a_deadline.insert(0, (d, deliveries))
                previous = d.deadline

            # After last deadline
            self.after_last_deadline = group.deliveries.filter(
                    time_of_delivery__gt=deadlines[numdeadlines - 1].deadline)
        else:
            self.ungrouped_deliveries = group.deliveries.order_by(
                    'time_of_delivery')

        """
        if numdeadlines > 0:
            deliveries = group.deliveries.filter(
                    time_of_delivery__lte = deadlines[0].deadline)

            # Within a deadline
            self.within_a_deadline.append((deadlines[0], deliveries))
            previous = deadlines[0].deadline
            for d in deadlines[1:]:
                deliveries = group.deliveries.filter(
                        time_of_delivery__lte = d.deadline,
                        time_of_delivery__gt = previous).order_by(
                                "-time_of_delivery")
                self.within_a_deadline.insert(0, (d, deliveries))
                previous = d.deadline

            # After last deadline
            self.after_last_deadline = group.deliveries.filter(
                    time_of_delivery__gt=deadlines[numdeadlines - 1].deadline)
        else:
            self.ungrouped_deliveries = group.deliveries.order_by(
                    'time_of_delivery')
        """
