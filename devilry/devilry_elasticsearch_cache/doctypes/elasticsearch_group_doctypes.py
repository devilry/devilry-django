from django.utils.translation import override
from elasticsearch_dsl import DocType, String, Nested

from devilry.apps.core import models as coremodels
from devilry.devilry_group import models as groupmodels
from devilry.devilry_elasticsearch_cache import elasticsearch_registry

import json

class AbstractAssignmentGroupRegistryItem(elasticsearch_registry.RegistryItem):
    """
    TODO: document
    """

    #: The model it should reflect. E.g: :class:`core.models.node.Node`
    modelclass = None

    #: The DocType(elasticsearch _doc_type) class it should reflect. Ex: :class:`.Node`
    doctype_class = None

    admins = Nested(
        properties={
            'id': String(fields={'raw': String(index='not_analyzed')})
        }
    )

    class Meta:
        abstract = True

    def get_search_text(self, modelobject):
        """
        Get searchable text consisting of short_name and long_name from this object
        and a unspecified number of parents.

        Examples:

            Typically something like this for a Period left to right where period is Spring 2001::

                "Spring 2001 spring2001 DUCK1010 - Objectoriented programming duck1010 Ifi ifi"

        This must be implemented in all subclasses.
        """
        raise NotImplementedError()

    def _get_parentnode_id(self, modelobject):
        """
        Returns parentnode id if modelobject has parent,
        else -1 is returned (topnode)
        """
        parent = modelobject.parentnode
        if parent is not None:
            return parent.id
        return -1

    def get_inherited_admins(self, modelobject):
        """
        Get a list of dictionaries containing the id(s) of admin(s)
        for this modelobject, where modelobject is e.g: :class:`core.models.node.Node`

        Example:

            This is what the field will look like in Elasticsearch::

                "admins": [
                    {\"id\": 1},
                    {\"id\": 2},
                    ...
                ]

        """
        # admins = []
        # for id in modelobject.get_all_admin_ids():
        #     admins.append(json.dumps({
        #     }))
        # for id in modelobject.get_all_admin_ids():
        #     self.admins.append({'id': id})

    def get_doctype_object_kwargs(self, modelobject):
        """
        Get the description fields for a DocType object where data for each field
        is aquired from the modelobject argument, where modelobject is e.g: :class:`core.models.node.Node`

        Example:

            Something like this::

                return {
                    '_id': modelobject.id,
                    'short_name': modelobject.short_name,
                    'long_name': modelobject.long_name,
                    'path': modelobject.get_path(),
                    'search_text': self.get_search_text(modelobject),
                }
        """

        return {
            '_id': modelobject.id,
            # 'parentnode_id': self.__get_parentnode_id(modelobject),
            # 'short_name': modelobject.short_displayname,
            # 'long_name': modelobject.long_displayname,
            'search_text': self.get_search_text(modelobject),
            'admins': self.get_inherited_admins(modelobject),
            # 'students': self._students_in_group_list(modelobject),
            # 'examiners': self._examiners_for_group_list(modelobject),
        }

    def to_doctype_object(self, modelobject):
        """
        TODO: document
        """
        return self.doctype_class(**self.get_doctype_object_kwargs(modelobject=modelobject))


class AssignmentGroup(DocType):
    class Meta:
        index = 'assignment_groups'


class AssignmentGroupRegistryItem(AbstractAssignmentGroupRegistryItem):
    """
    A RegistryItem class of :class:`coremodels.assignment.AssignmentGroup` that defines the properties of a :class:`.AssignmentGroup` as DocType.

    Is added to the :file:`.elasticsearch_registry.registry` singleton.
    """
    modelclass = coremodels.AssignmentGroup
    doctype_class = AssignmentGroup

    def _students_in_group_list(self, modelobject):
        return modelobject.get_students().split()

    def _examiners_for_group_list(self, modelobject):
        return modelobject.get_examiners().split()

    def get_search_text(self, modelobject):
        assignment_group = modelobject
        search_text = \
            u'{long_name} {short_name} ' \
            u'{assignment_long_name} {assignment_short_name} ' \
            u'{period_long_name} {period_short_name} ' \
            u'{subject_long_name} {subject_short_name} ' \
            u'{parentnode_long_name} {parentnode_short_name} '.format(
                short_name=assignment_group.long_displayname,
                long_name=assignment_group.short_displayname,
                assignment_long_name=assignment_group.assignment.long_name,
                assignment_short_name=assignment_group.assignment.short_name,
                period_long_name=assignment_group.assignment.period.long_name,
                period_short_name=assignment_group.assignment.period.short_name,
                subject_long_name=assignment_group.assignment.period.subject.long_name,
                subject_short_name=assignment_group.assignment.period.subject.short_name,
                parentnode_long_name=assignment_group.assignment.period.subject.parentnode.long_name,
                parentnode_short_name=assignment_group.assignment.period.subject.parentnode.short_name,)
        return search_text

    def get_doctype_object_kwargs(self, modelobject):
        kwargs = super(AssignmentGroupRegistryItem, self).get_doctype_object_kwargs(modelobject=modelobject)
        assignment_group = modelobject
        kwargs.update({
            'parentnode_id': self._get_parentnode_id(modelobject),
            'short_name': modelobject.short_displayname,
            'long_name': modelobject.long_displayname,
            'is_open': assignment_group.is_open,
            'etag': assignment_group.etag,
            'delivery_status': assignment_group.delivery_status,
            'students': self._students_in_group_list(modelobject),
            'examiners': self._examiners_for_group_list(modelobject),
        })
        return kwargs

    def get_all_modelobjects(self):
        return coremodels.AssignmentGroup.objects.select_related(
            'parentnode',  # Assignment
            'parentnode_parentnode',  # Period
            'parentnode_parentnode_parentnode',  # subject
            'parentnode_parentnode_parentnode_parentnode',  # parentnode of subject
        ).all()


elasticsearch_registry.registry.add(AssignmentGroupRegistryItem())


class FeedbackSet(DocType):
    class Meta:
        index = 'assignment_groups'


class FeedbackSetRegistryItem(AbstractAssignmentGroupRegistryItem):
    """
    TODO: Document
    """
    modelclass = groupmodels.FeedbackSet
    doctype_class = FeedbackSet

    def get_search_text(self, modelobject):
        return ''

    def get_doctype_object_kwargs(self, modelobject):
        kwargs=super(FeedbackSetRegistryItem, self).get_doctype_object_kwargs(modelobject=modelobject)
        feedback_set = modelobject
        kwargs.update({
            'parentnode_id': feedback_set.group.id,
            'points': feedback_set.points,
            'published_by': feedback_set.published_by.id,
            'created_by': feedback_set.created_by.id,
            'created_datetime': feedback_set.created_datetime,
            'published_datetime': feedback_set.published_datetime,
            'deadline_datetime': feedback_set.deadline_datetime,
        })
        return kwargs

    def get_all_modelobjects(self):
        return groupmodels.FeedbackSet.objects.select_related(
            'group', # AssignmentGroup
            'group_parentnode',  # Assignment
            'group_parentnode_parentnode',  # Period
            'group_parentnode_parentnode_parentnode',  # subject
            'group_parentnode_parentnode_parentnode_parentnode',  # parentnode of subject
        ).all()

elasticsearch_registry.registry.add(FeedbackSetRegistryItem())

class GroupComment(DocType):
    class Meta:
        index = 'assignment_groups'


class GroupCommentRegistryItem(AbstractAssignmentGroupRegistryItem):
    """
    TODO: Document
    """
    modelclass = groupmodels.GroupComment
    doctype_class = GroupComment

    def get_search_text(self, modelobject):
        return ''

    def get_doctype_object_kwargs(self, modelobject):
        kwargs=super(GroupCommentRegistryItem, self).get_doctype_object_kwargs(modelobject=modelobject)
        group_comment = modelobject
        kwargs.update({
            'parentnode_id': group_comment.feedback_set.id,
            'instant_publish': group_comment.instant_publish,
            'visible_for_students': group_comment.visible_for_students,
            'comment_text': group_comment.text,
            'user': group_comment.user.id,
            'parent_comment': group_comment.parent,
            'created_datetime': group_comment.created_datetime,
            'published_datetime': group_comment.published_datetime,
            'user_role': group_comment.user_role,
            'comment_type': group_comment.comment_type,
        })
        return kwargs

    def get_all_modelobjects(self):
        return groupmodels.GroupComment.objects.select_related(
            'feedback_set', # FeedbackSet
            'feedback_set_group_comment', # AssignmentGroup
            'feedback_set_group_parentnode',  # Assignment
            'feedback_set_group_parentnode_parentnode',  # Period
            'feedback_set_group_parentnode_parentnode_parentnode',  # subject
            'feedback_set_group_parentnode_parentnode_parentnode_parentnode',  # parentnode of subject
        ).all()

elasticsearch_registry.registry.add(GroupCommentRegistryItem())