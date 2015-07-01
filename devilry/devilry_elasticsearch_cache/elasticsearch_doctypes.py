from elasticsearch_dsl import DocType, String

from devilry.apps.core import models as coremodels
from devilry.devilry_elasticsearch_cache import elasticsearch_registry


class AbstractBaseNodeRegistryItem(elasticsearch_registry.RegistryItem):
    """
    TODO: Document
    """

    #: TODO - document
    modelclass = None

    #: TODO - document
    doctype_class = None

    def get_search_text(self, node):
        """
        TODO: document

        Examples:

            Typically something like this::

                dsajkdasj lkdjas dsakjlk oda
        """
        raise NotImplementedError()

    def get_doctype_object_kwargs(self, modelobject):
        """
        TODO: document
        """
        return {
            '_id': modelobject.id,
            'short_name': modelobject.short_name,
            'long_name': modelobject.long_name,
            'path': modelobject.get_path(),
            'search_text': self.get_search_text(modelobject)
        }

    def to_doctype_object(self, modelobject):
        """
        TODO: document
        """
        return self.doctype_class(**self.get_doctype_object_kwargs(modelobject=modelobject))


class Node(DocType):
    """
    TODO: Document
    """
    # short_name = String(index='not_analyzed')
    # long_name = String(index='not_analyzed')

    class Meta:
        index = 'devilry'


class NodeRegistryItem(AbstractBaseNodeRegistryItem):
    """
    TODO: Document
    """
    modelclass = coremodels.Node
    doctype_class = Node

    def get_search_text(self, modelobject):
        node = modelobject
        search_text = u'{long_name} {short_name}'.format(
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
    TODO: Document
    """
    class Meta:
        index = 'devilry'


class SubjectRegistryItem(AbstractBaseNodeRegistryItem):
    """
    TODO: Document
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
    TODO: Document
    """
    class Meta:
        index = 'devilry'


class PeriodRegistryItem(AbstractBaseNodeRegistryItem):
    """
    TODO: Document
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
