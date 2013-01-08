/** Breadcrumb management. */
Ext.define('devilry_header.Breadcrumbs', {
    extend: 'Ext.Component',
    alias: 'widget.breadcrumbs',
    cls: 'devilry_header_breadcrumbcomponent',

    requires: [
        'Ext.ComponentQuery'
    ],

    tpl: [
        '<ul class="devilry_header_breadcrumb">',
            '<tpl for="breadcrumbs">',
                '<tpl if="xindex != xcount">',
                    '<li>',
                        '<a href="{url}">{text}</a><span class="divider">/</span>',
                    '</li>',
                '</tpl>',
                '<tpl if="xindex == xcount">',
                    '<li class="active">{text}</li>',
                '</tpl>',
            '</tpl>',
        '</ul>'
    ],

    /**
     * @cfg {object} [defaultBreadcrumbs=undefined]
     * A list of breadcrumbs that will always be added to the beginning of
     * the breadcrumbs.
     */
    defaultBreadcrumbs: undefined,

    initComponent: function() {
        this.clear();
        this.callParent(arguments);
        this.draw();
    },

    /** Set the breadcrumbs.
     *
     * Example:
     *
     *      set([{
     *          url: '/hello',
     *          text: 'Hello'
     *      }, {
     *          url: '/hello/cruel',
     *          text: 'Cruel'
     *      }], 'World');
     * */
    set: function(breadcrumbs, current) {
        this.clear();
        if(this.getDefaultBreadcrumbs()) {
            this.addMany(this.getDefaultBreadcrumbs());
        }
        this.addMany(breadcrumbs);
        this.add('', current);
        this.draw();
    },

    /**
     * Get the default breadcrumbs. You can override this to generate
     * ``defaultBreadcrumbs`` dynamically. Defaults to returning
     * ``this.defaultBreadcrumbs``.
     */
    getDefaultBreadcrumbs:function () {
        return this.defaultBreadcrumbs;
    },

    addMany: function(breadcrumbs) {
        Ext.Array.each(breadcrumbs, function(breadcrumb) {
            this.add(breadcrumb.url, breadcrumb.text);
        }, this);
    },

    add: function(url, text) {
        this.breadcrumbs.push({
            url: url,
            text: text
        });
    },

    clear: function() {
        this.breadcrumbs = [];
    },

    draw: function() {
        if(this.breadcrumbs.length === 0) {
            this.hide();
        } else {
            this.show();
            this.update({
                breadcrumbs: this.breadcrumbs
            });
        }
    },

    setHome: function() {
        this.clear();
        this.draw();
    },

    statics: {
        /** Return the first detected instance of this component in body. */
        getInBody: function() {
            var components = Ext.ComponentQuery.query('breadcrumbs');
            if(components.length === 1) {
                return components[0];
            } else if(components.length === 0) {
                throw "Could not find any devilry_header.Breadcrumbs component in body.";
            } else {
                throw "Found more than one devilry_header.Breadcrumbs component in body.";
            }
        }
    }
});
