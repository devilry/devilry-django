Ext.define('themebase.SidebarTitle', {
    extend: 'themebase.CenterTitle',
    alias: 'widget.sidebartitle',

    tpl: ['<h2 class="sidebartitle">{title:ellipsis(25)}</h2>'],

    initComponent: function() {
        this.callParent(arguments);
    }
});
