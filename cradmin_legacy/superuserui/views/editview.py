from cradmin_legacy.superuserui.views import mixins
from cradmin_legacy.viewhelpers import update


class View(mixins.QuerySetForRoleMixin, update.UpdateView):
    enable_modelchoicefield_support = True
