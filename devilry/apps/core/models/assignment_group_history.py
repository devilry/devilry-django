import json

from django.db import models
from django.utils.timezone import datetime

class AssignmentGroupHistory(models.Model):
    """

    """

    #: OneToOneFiled :class:`core.AssignmentGroup`
    assignment_group = models.OneToOneField("AssignmentGroup")

    DEFAULT_MERGE_HISTORY_JSON = {
        'merge_datetime': None,
        'state': None,
        'from': None,
        'to': None
    }

    #: The merge history for the one to one field :class:`core.AssignmentGroupHistory.assignment_group`
    #: will be stored inn a tree structure
    #: {
    #:  'merge_datetime': datetime of merge,
    #:  'state': state of assignment group before merge
    #:  'from': history,
    #:  'to': history,
    #: }
    merge_history_json = models.TextField(
        null=False, blank=False, default=json.dumps(DEFAULT_MERGE_HISTORY_JSON)
    )

    @property
    def merge_history(self):
        """
        Decode :obj:`.AssignmentGroupHistory.merge_history_json` using `json.loads`
        and return the result

        Returns:
            'None' if merge_history_json is empty
        """

        if self.merge_history_json:
            if not hasattr(self, '_merge_history'):

                self._merge_history = json.loads(self.merge_history_json)

            return self._merge_history
        else:
            return None

    @merge_history.setter
    def merge_history(self, merge_history):
        """
        Set :obj:`.AssignmentGroupHistory.merge_history_json`.  Encodes the given
        dictionary using `json.dumps`
        Args:
            merge_history: dictionary

        Returns:

        """
        self.merge_history_json = json.dumps(merge_history)
        if hasattr(self, '_merge_history'):
            delattr(self, '_merge_history')
        if hasattr(self, '_meta_data'):
            delattr(self, '_meta_data')

    def _meta_data_bfs(self):
        """
        Creating a flat list with metedata of all merges with breadth first search.

        Returns:
            A flat list with metadata of all merges in the merge history json tree
        """
        meta_data = []
        queue = []
        queue.append(self.merge_history)
        while queue:
            merge = queue.pop(0)
            if not merge['merge_datetime']:
                continue

            meta_data.append({
                'merge_datetime': merge['merge_datetime'],
                'from_name': merge['from']['state']['name'],
                'to_name': merge['to']['state']['name']
            })

            queue.append(merge['from'])
            queue.append(merge['to'])
        return meta_data

    @property
    def meta_data(self):
        """
        returns a flat list with metadata of merges

        Returns:
            flat list
        """
        if not hasattr(self, '_meta_data'):
            self._meta_data = self._meta_data_bfs()
        return self._meta_data

    def _make_default_merge_history(self):
        """
        Makes default merge history dict
        """
        return {
            'merge_datetime': None,
            'state': None,
            'from': None,
            'to': None
        }

    def merge_assignment_group_history(self, source):
        """
        Creates a new AssignmentGroupHistory with merged history from self and target

        Args:
            source: :class:`.AssignmentGroup`

        Returns:
            :class:`.AssignmentGroupHistory`

        """
        newhistory = self._make_default_merge_history()
        newhistory['to'] = self.merge_history
        newhistory['to']['state'] = self.assignment_group.get_current_state()
        newhistory['merge_datetime'] = datetime.now().isoformat()

        try:
            sourcehistory = source.assignmentgrouphistory
        except AssignmentGroupHistory.DoesNotExist:
            newhistory['from'] = self._make_default_merge_history()
        else:
            newhistory['from'] = sourcehistory.merge_history

        newhistory['from']['state'] = source.get_current_state()
        self.merge_history = newhistory

