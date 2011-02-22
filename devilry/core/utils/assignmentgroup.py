class GroupDeliveriesByDeadline():
    def __init__(self, group):
        self.groups = []
        deadlines = group.deadlines.all().order_by('deadline')
        for dl in deadlines:
            deliveries = dl.deliveries.order_by("-time_of_delivery")
            if dl.is_head and len(deliveries) == 0:
                continue
            self.groups.insert(0, (dl, deliveries))
            
