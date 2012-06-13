/** Breadcrumb management. */
Ext.define('devilry_extjsextras.Breadcrumbs', {
    extend: 'Ext.Component',
    alias: 'widget.breadcrumbs',
    cls: 'breadcrumb-component',

    home: {
        url: '',
        text: 'Dashboard'
    },

    tpl: [
        '<ul class="breadcrumb">',
            '<li class="prefixtext">',
                dtranslate('devilry_extjsextras.breadcrumb.prefixtext'),
            ':</li>',
            '<tpl for="breadcrumbs">',
                '<tpl if="xindex != xcount">',
                    '<li>',
                        '<a href="#{url}">{text}</a><span class="divider">/</span>',
                    '</li>',
                '</tpl>',
                '<tpl if="xindex == xcount">',
                    '<li class="active">{text}</li>',
                '</tpl>',
            '</tpl>',
        '<ul>'
    ],

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
        Ext.Array.each(breadcrumbs, function(breadcrumb) {
            this.add(breadcrumb.url, breadcrumb.text);
        }, this);
        this.add('', current)
        this.draw();
    },

    add: function(url, text) {
        this.breadcrumbs.push({
            url: url,
            text: text
        });
    },

    clear: function() {
        this.breadcrumbs = [];
        //this.add(this.home.url, this.home.text);
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
    }
});
