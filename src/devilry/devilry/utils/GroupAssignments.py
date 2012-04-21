import OrderedDict


def group_assignmentgroups(assignment_groups):
    
    dict = OrderedDict()

    for group in assignment_groups:
        
        if not dict.has_key(group.parentnode.parentnode.parentnode):
            subject = Subject(group.parentnode.parentnode.parentnode.short_name)
            dict[group.parentnode.parentnode.parentnode] = subject

        dict[group.parentnode.parentnode.parentnode].add_period(group)

    return dict.values()


def group_assignments(assignments):
    
    dict = OrderedDict()

    for group in assignments:
        
        if not dict.has_key(group.parentnode.parentnode.parentnode):
            subject = Subject(group.parentnode.parentnode.parentnode.short_name)
            dict[group.parentnode.parentnode.parentnode] = subject

        dict[group.parentnode.parentnode.parentnode].add_period(group)

    return dict.values()

class Subject(object):

    def __init__(self, name):
        self.periods = OrderedDict()
        self.name = name
            
    def __str__(self):
        return self.name

    def add_period(self, assignment_group):
        
        if not self.periods.has_key(assignment_group.parentnode.parentnode):
            period = Period(assignment_group.parentnode.parentnode.short_name)
            self.periods[assignment_group.parentnode.parentnode] = period

        self.periods[assignment_group.parentnode.parentnode].add_assignment(assignment_group)

    def __iter__(self):
        return iter(self.periods.values())


class Period(object):

    def __init__(self, name):
        self.assignments = list()
        self.name = name
    
    def __str__(self):
        return self.name

    def add_assignment(self, assignment_group):
        self.assignments.append(assignment_group)

    def __iter__(self):
        return iter(self.assignments)
