Ext.define('themebase.view.Breadcrumbs', {
    extend: 'Ext.Component',
    alias: 'widget.breadcrumbs',
    cls: 'breadcrumb-component',

    home: ['', 'Dashboard'],

    tpl: new Ext.XTemplate([
        '<ul class="breadcrumb">',
        '    <tpl for="breadcrumbs">',
        '       <tpl if="xindex != xcount">',
        '           <li>',
        '               <a href="#{url}">{text}</a><span class="divider">/</span>',
        '           </li>',
        '       </tpl>',
        '       <tpl if="xindex == xcount">',
        '           <li class="active">{text}</li>',
        '       </tpl>',
        '    </tpl>',
        '<ul>'
    ]),

    initComponent: function() {
        this.clear();
        this.callParent(arguments);
        this.draw();
    },

    set: function(breadcrumbs, current) {
        this.clear();
        Ext.Array.each(breadcrumbs, function(breadcrumb) {
            this.add(breadcrumb[0], breadcrumb[1]);
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
        this.add(this.home[0], this.home[1]);
    },

    draw: function() {
        this.update({
            breadcrumbs: this.breadcrumbs
        });
    }
});
