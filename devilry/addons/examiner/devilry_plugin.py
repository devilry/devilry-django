from devilry.addons.quickdash.dashboardplugin_registry import (registry, 
        DashboardView)

import dashboardviews


registry.add_view(DashboardView(dashboardviews.list_assignments))
