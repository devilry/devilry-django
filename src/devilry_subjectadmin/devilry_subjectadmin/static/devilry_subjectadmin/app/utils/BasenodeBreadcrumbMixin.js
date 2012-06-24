/**
 * Mixin for basenode controllers that need to set the breadcrumb.
 */
Ext.define('devilry_subjectadmin.utils.BasenodeBreadcrumbMixin', {
    requires: ['devilry_subjectadmin.utils.UrlLookup'],

    setBreadcrumb: function(basenodeRecord) {
        var breadcrumb = [{
            text: gettext("All subjects"),
            url: '/'
        }];

        Ext.each(basenodeRecord.get('breadcrumb'), function(item) {
            var url;
            try {
                url = devilry_subjectadmin.utils.UrlLookup.overviewByType(item.type, item.id);
            } catch(e) {
                url = '/doesnotexist' // TODO: Do not catch this exception when all overviews are in place
            }
            breadcrumb.push({
                text: item.short_name,
                url: url
            });
        });

        this.application.breadcrumbs.set(breadcrumb, basenodeRecord.get('short_name'));
    },

    setLoadingBreadcrumb: function() {
        this.application.breadcrumbs.set([], gettext('Loading ...'));
    }
});
