/**
 * Defines a box that lists the location of a basenode in the node hierarchy.
 * */
Ext.define('devilry_subjectadmin.view.BaseNodeHierLocation', {
    extend: 'Ext.Panel',
    alias: 'widget.basenodehierlocation',
    bodyCls: 'devilry_basenodehierlocation bootstrap',
    title: gettext('Location in hierarchy'),
    ui: 'lookslike-parawitheader-panel',
    requires: ['devilry_subjectadmin.utils.UrlLookup'],

    listingTpl: [
        '<ul>',
            '<tpl for="breadcrumb">',
                '<li>',
                    '<a href="{url}">{text}</a>',
                '</li>',
            '</tpl>',
            '<li class="current">{short_name}</li>',
        '</ul>'
    ],

    _get_data: function(basenodeRecord) {
        var data = [];
        Ext.each(basenodeRecord.get('breadcrumb'), function(item) {
            var url = devilry_subjectadmin.utils.UrlLookup.overviewByType(item.type, item.id);
            data.push({
                text: item.short_name,
                url: url
            });
        }, this);
        return data;
    },

    /**
     * @param {Object} basenodeRecord (required)
     * A basenode record with a ``breadcrumb`` field.
     */
    setLocation: function(basenodeRecord) {
        this.update(Ext.create('Ext.XTemplate', this.listingTpl).apply({
            breadcrumb: this._get_data(basenodeRecord),
            short_name: basenodeRecord.get('short_name')
        }));
    }
});
