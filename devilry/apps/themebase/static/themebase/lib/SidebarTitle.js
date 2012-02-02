Ext.define('themebase.SidebarTitle', {
    extend: 'themebase.CenterTitle',
    alias: 'widget.sidebartitle',

    tpl: ['<h2 class="sidebartitle">{title}</h2>'],

    initComponent: function() {
        this.title = Ext.String.ellipsis(this.title, 20);
        this.callParent(arguments);
    }
});
