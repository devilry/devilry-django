Ext.define('subjectadmin.view.action.List' ,{
    extend: 'Ext.Component',
    alias: 'widget.actionlist',

    /**
     * @cfg
     * 
     */
    links: [],

    html: 'List',
    
    initComponent: function() {
        Ext.Array.each(this.links, function(link) {
            console.log(link);
        });
        this.callParent(arguments);
    }
});
