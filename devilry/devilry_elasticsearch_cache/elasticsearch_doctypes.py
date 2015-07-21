from elasticsearch_dsl import DocType, String, Nested
from django.contrib.auth import models

from devilry.apps.core import models as coremodels
from devilry.devilry_elasticsearch_cache import elasticsearch_registry

import json


class AbstractBaseNodeRegistryItem(elasticsearch_registry.RegistryItem):
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

    def __get_parentnode_id(self, modelobject):
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
        #admins = []
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

        self.get_inherited_admins(modelobject)

        return {
            '_id': modelobject.id,
            'parentnode_id': self.__get_parentnode_id(modelobject),
            'short_name': modelobject.short_name,
            'long_name': modelobject.long_name,
            'path': modelobject.get_path(),
            'search_text': self.get_search_text(modelobject),
            'admins': self.admins,
            #'admins': self.get_inherited_admins(modelobject),
        }

    def to_doctype_object(self, modelobject):
        """
        TODO: document
        """
        return self.doctype_class(**self.get_doctype_object_kwargs(modelobject=modelobject))


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

    def __get_parentnode_id(self, modelobject):
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
        #admins = []
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

        self.get_inherited_admins(modelobject)

        return {
            '_id': modelobject.id,
            'parentnode_id': self.__get_parentnode_id(modelobject),
            'name': modelobject.name,
            'path': 'PATH NEEDED?',
            'search_text': self.get_search_text(modelobject),
            'admins': self.admins,
            #'admins': self.get_inherited_admins(modelobject),
        }

    def to_doctype_object(self, modelobject):
        """
        TODO: document
        """
        return self.doctype_class(**self.get_doctype_object_kwargs(modelobject=modelobject))


class Node(DocType):
    """
    Class to represent a Node from :class:`devilry.apps.core.models.node.Node`
    """
    # short_name = String(index='not_analyzed')
    # long_name = String(index='not_analyzed')

    class Meta:
        index = 'basenodes'


class NodeRegistryItem(AbstractBaseNodeRegistryItem):
    """
    A RegistryItem class of :class:`core.models.node.Node` that defines the properties of a :class:`.Node` as DocType.

    Is added to the :file:`.elasticsearch_registry.registry` singleton.
    """
    modelclass = coremodels.Node
    doctype_class = Node

    def get_search_text(self, modelobject):
        node = modelobject
        search_text = \
            u'{long_name} {short_name}'.format(
                long_name=node.long_name,
                short_name=node.short_name)
        if node.parentnode_id is not None:
            search_text = u'{} {}'.format(search_text,
                                          self.get_search_text(node.parentnode))
        return search_text

    def get_all_modelobjects(self):
        return coremodels.Node.objects.select_related('parentnode').all()

elasticsearch_registry.registry.add(NodeRegistryItem())


class Subject(DocType):
    """
    Class to represent a Subject from :class:`devilry.apps.core.models.subject.Subject`
    """
    class Meta:
        index = 'basenodes'


class SubjectRegistryItem(AbstractBaseNodeRegistryItem):
    """
    A RegistryItem class of :class:`core.models.subject.Subject` that defines the properties of a :class:`.Subject` as DocType.

    Is added to the :file:`.elasticsearch_registry.registry` singleton.
    """
    modelclass = coremodels.Subject
    doctype_class = Subject

    def get_search_text(self, modelobject):
        subject = modelobject
        search_text = \
            u'{long_name} {short_name} ' \
            u'{parentnode_long_name} {parentnode_short_name}'.format(
                long_name=subject.long_name,
                short_name=subject.short_name,
                parentnode_long_name=subject.parentnode.long_name,
                parentnode_short_name=subject.parentnode.short_name)
        return search_text

    def get_all_modelobjects(self):
        return coremodels.Subject.objects.select_related('parentnode').all()

elasticsearch_registry.registry.add(SubjectRegistryItem())


class Period(DocType):
    """
    Class to represent a Period from :class:`devilry.apps.core.models.period.Period`
    """
    class Meta:
        index = 'basenodes'


class PeriodRegistryItem(AbstractBaseNodeRegistryItem):
    """
    A RegistryItem class of :class:`core.models.period.Period` that defines the properties of a :class:`.Period` as DocType.

    Is added to the :file:`.elasticsearch_registry.registry` singleton.
    """
    modelclass = coremodels.Period
    doctype_class = Period

    def get_search_text(self, modelobject):
        period = modelobject
        search_text = \
            u'{long_name} {short_name} ' \
            u'{subject_long_name} {subject_short_name} ' \
            u'{parentnode_long_name} {parentnode_short_name}'.format(
                long_name=period.long_name,
                short_name=period.short_name,
                subject_long_name=period.subject.long_name,
                subject_short_name=period.subject.short_name,
                parentnode_long_name=period.subject.parentnode.long_name,
                parentnode_short_name=period.subject.parentnode.short_name)
        return search_text

    def get_doctype_object_kwargs(self, modelobject):
        kwargs = super(PeriodRegistryItem, self).get_doctype_object_kwargs(modelobject=modelobject)
        period = modelobject
        kwargs.update({
            'start_time': period.start_time,
            'end_time': period.end_time,
        })
        return kwargs

    def get_all_modelobjects(self):
        return coremodels.Period.objects.select_related(
            'parentnode',  # Subject
            'parentnode__parentnode'  # Parentnode of subject
        ).all()

elasticsearch_registry.registry.add(PeriodRegistryItem())


class Assignment(DocType):
    class Meta:
        index = 'basenodes'


class AssignmentRegistryItem(AbstractBaseNodeRegistryItem):
    """
    A RegistryItem class of :class:`coremodels.assignment.Assignment` that defines the properties of a :class:`.Assignment` as DocType.

    Is added to the :file:`.elasticsearch_registry.registry` singleton.
    """
    modelclass = coremodels.Assignment
    doctype_class = Assignment

    def get_search_text(self, modelobject):
        assignment = modelobject
        search_text = \
            u'{long_name} {short_name} ' \
            u'{subject_long_name} {subject_short_name} ' \
            u'{parentnode_long_name} {parentnode_short_name} ' \
            u'{parentnode_parentnode_long_name} {parentnode_parentnode_short_name}'.format(
                long_name=assignment.long_name,
                short_name=assignment.short_name,
                subject_long_name=assignment.period.long_name,
                subject_short_name=assignment.period.short_name,
                parentnode_long_name=assignment.period.subject.long_name,
                parentnode_short_name=assignment.period.subject.short_name,
                parentnode_parentnode_long_name=assignment.period.subject.parentnode.long_name,
                parentnode_parentnode_short_name=assignment.period.subject.parentnode.short_name)
        return search_text

    def get_doctype_object_kwargs(self, modelobject):
        kwargs = super(AssignmentRegistryItem, self).get_doctype_object_kwargs(modelobject=modelobject)
        assignment = modelobject
        kwargs.update({
            'publishing_time': assignment.publishing_time,
            'anonymous': assignment.anonymous,
            'students_can_see_points': assignment.students_can_see_points,
            'delivery_types': assignment.delivery_types,
            'deadline_handling': assignment.deadline_handling,
            'scale_points_percent': assignment.scale_points_percent,
            'first_deadline': assignment.first_deadline,
            'max_points': assignment.max_points,
            'passing_grade_min_points': assignment.passing_grade_min_points,
            'points_to_grade_mapper': assignment.points_to_grade_mapper,
            'grading_system_plugin_id': assignment.grading_system_plugin_id,
            'students_can_create_groups': assignment.students_can_create_groups,
            'students_can_not_create_groups_after': assignment.students_can_not_create_groups_after,
            'feedback_workflow': assignment.feedback_workflow,
        })
        return kwargs

    def get_all_modelobjects(self):
        return coremodels.Assignment.objects.select_related(
            'parentnode', # Period
            'parentnode_parentnode', # parentnode of subject
            'parentnode_parentnode_parentnode', # parentnode of subjects parentnode
        ).all()

elasticsearch_registry.registry.add(AssignmentRegistryItem())


class AssignmentGroup(DocType):
    class Meta:
        index = 'AssignmentGroups'


class AssignmentGroupRegistryItem(AbstractAssignmentGroupRegistryItem):
    """
    TODO: Document
    """
    modelclass = coremodels.AssignmentGroup
    doctype_class = AssignmentGroup

    def get_search_text(self, modelobject):
        assignment_group = modelobject
        search_text = \
            u'{name} ' \
            u'{subject_long_name} {subject_short_name} ' \
            u'{parentnode_long_name} {parentnode_short_name} ' \
            u'{parentnode_parentnode_long_name} {parentnode_parentnode_short_name} '.format(
                name=assignment_group.name,
                assignment_long_name=assignment_group.assignment.long_name,
                assignment_short_name=assignment_group.assignment.short_name,
                subject_long_name=assignment_group.assignment.period.long_name,
                subject_short_name=assignment_group.assignment.period.short_name,
                parentnode_long_name=assignment_group.assignment.period.subject.long_name,
                parentnode_short_name=assignment_group.assignment.period.subject.short_name,
                parentnode_parentnode_long_name=assignment_group.assignment.period.subject.parentnode.long_name,
                parentnode_parentnode_short_name=assignment_group.assignment.period.subject.parentnode.short_name)
        return search_text

    def get_doctype_object_kwargs(self, modelobject):
        kwargs = super(AssignmentGroupRegistryItem, self).get_doctype_object_kwargs(modelobject=modelobject)
        assignment_group = modelobject
        kwargs.update({
            'name': assignment_group.name,
            'is_open': assignment_group.is_open,
            'etag': assignment_group.etag,
            'delivery_status': assignment_group.delivery_status,
        })

    def get_all_modelobjects(self):
        return coremodels.AssignmentGroup.objects.select_related(
            'parentnode', # Assignment
            'parentnode_parentnode', # Period
            'parentnode_parentnode_parentnode', # subject
            'parentnode_parentnode_parentnode_parentnode', # parentnode of subject
        )

elasticsearch_registry.registry.add(AssignmentGroupRegistryItem())