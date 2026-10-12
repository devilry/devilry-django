from cradmin_legacy.superuserui.views import mixins
from cradmin_legacy.viewhelpers import delete


class View(mixins.QuerySetForRoleMixin, delete.DeleteView):
    pass
