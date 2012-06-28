/**
 * Mixin for basenode controllers that need to set the breadcrumb.
 */
Ext.define('devilry_subjectadmin.utils.BasenodeBreadcrumbMixin', {
    requires: ['devilry_subjectadmin.utils.UrlLookup'],

    setBreadcrumb: function(basenodeRecord) {
        var breadcrumb = [{
            text: gettext("All subjects"),
            url: '#/'
        }];

        Ext.each(basenodeRecord.get('breadcrumb'), function(item) {
            var ignore = item.type === 'Node';
            if(!ignore) {
                var url = devilry_subjectadmin.utils.UrlLookup.overviewByType(item.type, item.id);
                breadcrumb.push({
                    text: item.short_name,
                    url: url
                });
            }
        });

        this.application.breadcrumbs.set(breadcrumb, basenodeRecord.get('short_name'));
    },

    setLoadingBreadcrumb: function() {
        this.application.breadcrumbs.set([], gettext('Loading ...'));
    },

    getPathFromBreadcrumb: function(basenodeRecord) {
        var path = '';
        Ext.Array.each(basenodeRecord.get('breadcrumb'), function(item) {
            if(item.type === 'Node') {
                return false; // break
            }
            console.log(item.short_name);
            path = item.short_name + '.' + path;
        }, this, true);
        return path + '.' + basenodeRecord.get('short_name');
    }
});
