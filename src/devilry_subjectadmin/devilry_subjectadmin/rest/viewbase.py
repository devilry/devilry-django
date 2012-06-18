from djangorestframework.views import ModelView, InstanceModelView
from djangorestframework.mixins import ListModelMixin

from .mixins import BaseNodeInstanceRestMixin
from .mixins import SelfdocumentingBaseNodeMixin


class ListOrCreateSubjectView(SelfdocumentingBaseNodeMixin, ListModelMixin, ModelView):
    def get_queryset(self):
        qry = self.resource.model.where_is_admin_or_superadmin(self.user)
        qry = qry.order_by('short_name')
        return qry

    def get_restdocs(self):
        return """
        List the {modelname} where the authenticated user is admin.

        ## Returns
        List of maps/dicts with the following attributes:
        {responsetable}
        """

    def postprocess_docs(self, docs):
        return docs.format(modelname=self.resource.model.__name__,
                           responsetable=self.htmldoc_responsetable())


class BaseNodeInstanceModelView(BaseNodeInstanceRestMixin,
                                SelfdocumentingBaseNodeMixin, InstanceModelView):
    def get_restdocs(self):
        return """
        Get info about the {modelname} and its admins.

        ## Returns
        Map/dict with the following attributes:
        {responsetable}
        """

    def put_restdocs(self):
        return """
        Update the {modelname} and its admins.

        ## Parameters
        {paramteterstable}
        """

    def delete_restdocs(self):
        return """
        Delete the {modelname}. Only possible if the authenticated user is
        superadmin, or if the {modelname} is empty.

        ## Returns
        Map/dict with a single attribute:
        {delete_responsetable}
        """

    def postprocess_docs(self, docs):
        return docs.format(modelname=self.resource.model.__name__,
                           paramteterstable=self.htmldoc_parameterstable(),
                           responsetable=self.htmldoc_responsetable(),
                           delete_responsetable=self.htmldoc_responsetable())
