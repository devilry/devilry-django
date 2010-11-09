class GroupDeliveriesByDeadline():
    def __init__(self, group):
        self.after_last_deadline = []
        self.within_a_deadline = []
        self.ungrouped_deliveries = []
        deadlines = group.deadlines.all().order_by('-deadline')
        numdeadlines = len(deadlines)
        if numdeadlines > 0:
            deliveries = group.deliveries.filter(
                    time_of_delivery__lte = deadlines[0].deadline)

            # Within a deadline
            self.within_a_deadline.append((deadlines[0], deliveries))
            previous = deadlines[0].deadline
            for d in deadlines[1:]:
                deliveries = group.deliveries.filter(
                        time_of_delivery__lte = d.deadline,
                        time_of_delivery__gt = previous)
                self.within_a_deadline.append((d, deliveries))
                previous = d.deadline

            # After last deadline
            self.after_last_deadline = group.deliveries.filter(
                    time_of_delivery__gt=deadlines[0].deadline)
        else:
            self.ungrouped_deliveries = group.deliveries.order_by(
                    'time_of_delivery')
