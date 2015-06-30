from django.utils import timezone
from devilry.apps.core.models import node
from devilry.apps.core.models import subject
from devilry.apps.core.models import period
from devilry.apps.core.models import assignment
from django.db import models


class NodeGenerator(object):

    def generate_hierarchy(self):
        '''
        Generates a hierarchy of nodes, starting with UiO as topnode then a Subject,
        Period, and Assignment in that order.

        Returns the node hierarchy
        '''
        top_node = node.Node()
        top_node.short_name = 'uio'
        top_node.long_name = 'UiO'
        top_node.id = 1

        subject_node = subject.Subject()
        subject_node.short_name = 'duck1010'
        subject_node.long_name = 'DUCK1010 DuckOriented Programming'
        subject_node.id = 2

        period_node = period.Period()
        period_node.short_name = '2015'
        period_node.start_time = timezone.now()
        period_node.id = 3

        assignment_node = assignment.Assignment()
        assignment_node.short_name = 'oblig 1'
        assignment_node.long_name = 'Oblig 1 Learn duck'
        assignment_node.id = 4

        assignment_node.parentnode = period_node
        period_node.parentnode = subject_node
        subject_node.parentnode = top_node

        return assignment_node

