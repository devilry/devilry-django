from djangorestframework.views import ModelView, InstanceModelView

from .mixins import BaseNodeInstanceRestMixin
from .mixins import SelfdocumentingBaseNodeMixin
from .mixins import BaseNodeListModelMixin
from .mixins import BaseNodeCreateModelMixin


class BaseNodeListOrCreateView(SelfdocumentingBaseNodeMixin, BaseNodeListModelMixin, BaseNodeCreateModelMixin, ModelView):
    """
    """


class BaseNodeInstanceModelView(BaseNodeInstanceRestMixin,
                                SelfdocumentingBaseNodeMixin, InstanceModelView):
    def get_restdocs(self):
        return """
        Get info about the {modelname} and its admins.

        # Returns
        Map/dict with the following attributes:
        {responsetable}
        """

    def put_restdocs(self):
        return """
        Update the {modelname} and its admins.

        # Parameters
        {update_parameterstable}
        """

    def delete_restdocs(self):
        return """
        Delete the {modelname}. Only possible if the authenticated user is
        superadmin, or if the {modelname} is empty.

        # Returns
        Map/dict with a single attribute:
        {delete_responsetable}
        """

    def postprocess_docs(self, docs):
        return docs.format(modelname=self.resource.model.__name__,
                           update_parameterstable=self.htmldoc_parameterstable(),
                           responsetable=self.htmldoc_responsetable(),
                           delete_responsetable=self.htmldoc_responsetable())
