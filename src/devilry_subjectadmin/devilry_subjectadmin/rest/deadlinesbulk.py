from datetime import datetime
from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated
from .auth import IsAssignmentAdmin

from devilry.apps.core.models import Deadline
from devilry.utils.restformat import format_datetime
from devilry.utils.restformat import format_timedelta
from .log import logger



class DeadlinesBulkRest(View):
    """
    List all deadlines on an assignment with newest deadline firsts. Deadlines
    with exactly the same ``deadline`` and ``text`` are collapsed into a single
    entry in the list, with the number of groups listed.
    """
    permissions = (IsAuthenticated, IsAssignmentAdmin)

    def _serialize_deadline(self, deadline):
        """
        Serialize ``Deadline``-object as plain python.
        """
        return {'deadline': format_datetime(deadline.deadline),
                'in_the_future': deadline.deadline > self.now,
                'offset_from_now': format_timedelta(self.now - deadline.deadline),
                'text': deadline.text}

    def _get_distinct_deadlines(self, deadlines):
        distinct_deadlines = {}
        keyformat = '{deadline}:{text}'
        for deadline in deadlines:
            key = keyformat.format(deadline=deadline.deadline, text=deadline.text)
            if key in distinct_deadlines:
                distinct_deadlines[key]['groupcount'] += 1
            else:
                serialized_deadline = self._serialize_deadline(deadline)
                serialized_deadline['groupcount'] = 1
                distinct_deadlines[key] = serialized_deadline
        return distinct_deadlines.values()

    def _deadline_cmp(self, a, b):
        comp = cmp(b['deadline'], a['deadline']) # Order with newest first
        if comp == 0:
            # Order by text if deadline is equal. text==None will be last in the list
            return cmp(a['text'], b['text'])
        else:
            return comp

    def _aggregate_deadlines(self):
        deadlines = Deadline.objects.filter(assignment_group__parentnode=self.assignment_id)
        distinct_deadlines = self._get_distinct_deadlines(deadlines)
        distinct_deadlines.sort(self._deadline_cmp)
        return distinct_deadlines

    def get(self, request, id):
        self.assignment_id = id
        self.now = datetime.now()
        distinct_deadlines = self._aggregate_deadlines()
        return {'deadlines': distinct_deadlines}
