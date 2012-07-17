/**
 * Mixin for basenode controllers that need to set the breadcrumb.
 */
Ext.define('devilry_subjectadmin.utils.BasenodeBreadcrumbMixin', {
    requires: ['devilry_subjectadmin.utils.UrlLookup'],

    _getBreadcrumbPrefix: function() {
        return [{
            text: gettext("All subjects"),
            url: '#/'
        }];
    },

    _addBasenodeBreadcrumbToBreadcrumb: function(breadcrumb, basenodeRecord) {
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
    },

    setBreadcrumb: function(basenodeRecord) {
        var breadcrumb = this._getBreadcrumbPrefix();
        this._addBasenodeBreadcrumbToBreadcrumb(breadcrumb, basenodeRecord);
        this.application.breadcrumbs.set(breadcrumb, basenodeRecord.get('short_name'));
    },

    /** For children of basenodes */
    setSubviewBreadcrumb: function(basenodeRecord, basenodeType, extra, current) {
        var breadcrumb = this._getBreadcrumbPrefix();
        this._addBasenodeBreadcrumbToBreadcrumb(breadcrumb, basenodeRecord);
        breadcrumb.push({
            text: basenodeRecord.get('short_name'),
            url: devilry_subjectadmin.utils.UrlLookup.overviewByType(basenodeType, basenodeRecord.get('id'))
        });
        breadcrumb = breadcrumb.concat(extra);
        this.application.breadcrumbs.set(breadcrumb, current);
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
            path = item.short_name + '.' + path;
        }, this, true);
        return path + basenodeRecord.get('short_name');
    }
});
