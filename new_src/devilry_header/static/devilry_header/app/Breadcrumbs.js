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
                        '<tpl for=".">',
                            '<tpl if="xindex &gt; 1">',
                                ' | ',
                            '</tpl>',
                            '<a href="{url}">{text}</a>',
                        '</tpl>',
                        '<span class="divider">/</span>',
                    '</li>',
                '</tpl>',
                '<tpl if="xindex == xcount">',
                    '<li class="active">{[this.getFirstText(values)]}</li>',
                '</tpl>',
            '</tpl>',
        '</ul>', {
            isMultiChoice: function(choices) {
                return choices.length > 1;
            },
            getFirstText: function(choices) {
                return choices[0].text;
            }
        }
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
        var defaultBreadcrumbs = this.getDefaultBreadcrumbs();
        if(defaultBreadcrumbs) {
            this.addMany(defaultBreadcrumbs);
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
            if(Ext.isArray(breadcrumb)) {
                this.addMultiChoice(breadcrumb);
            } else {
                this.add(breadcrumb.url, breadcrumb.text);
            }
        }, this);
    },

    /**
     * Called every time an url is added to the breadcrumb. Override it
     * if you want to change the URLs (I.E.: Add a prefix).
     */
    formatUrl: function (url, meta) {
        return url;
    },

    /**
     * Add breadcrumb.
     * @param url The URL of the breadcrumb.
     * @param text The text for the breadcrumb.
     * @param meta Metadata that can be used by other systems when to customize the breadcrumb.
     */
    add: function(url, text, meta) {
        this.addMultiChoice([{
            url: this.formatUrl(url),
            text: text,
            meta: meta
        }]);
    },

    addMultiChoice: function(choices) {
        this.breadcrumbs.push(choices);
    },

    clear: function() {
        this.breadcrumbs = [];
    },

    draw: function() {
        var header2el = Ext.get('devilry_header2');
        var header2Component = null;
        if(!Ext.isEmpty(header2el)) {
            var components = Ext.ComponentQuery.query('devilryheader2');
            if(components.length == 1) {
                header2Component = components[0];
            }
        } else {
            console.warn('Could not find #devilry_header2 when drawing the breadcrumb.')
        }

        if(this.breadcrumbs.length === 0) {
            this.hide();
            if(header2Component != null) {
                header2Component.resizeHeaderForNoBreadcrumbs();
            }
        } else {
            this.show();
            this.update({
                breadcrumbs: this.breadcrumbs
            });
            if(header2Component != null) {
                header2Component.resizeHeaderForBreadcrumbs();
            }
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
