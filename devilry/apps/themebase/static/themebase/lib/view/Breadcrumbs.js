Ext.define('themebase.view.Breadcrumbs', {
    extend: 'Ext.Component',
    alias: 'widget.breadcrumbs',
    cls: 'breadcrumb-component',

    home: {
        url: '',
        text: 'Dashboard'
    },

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
        this.add(this.home.url, this.home.text);
    },

    draw: function() {
        this.update({
            breadcrumbs: this.breadcrumbs
        });
    },

    setHome: function() {
        this.clear();
        this.draw();
    }
});
