/**
 * Ext.menu.Menu with utilities that simplify dynamically loading the items.
 */
Ext.define('devilry_subjectadmin.view.managestudents.DynamicLoadMenu' ,{
    extend: 'Ext.menu.Menu',
    alias: 'widget.dynamicloadmenu',
    cls: 'devilry_subjectadmin_dynamicloadmenu',
    plain: true,

    initComponent: function() {
        this.callParent(arguments);
        this.setLoadingString();
    },

    setLoadingString: function() {
        this.setItems([
            gettext('Loading') + ' ...'
        ]);
    },

    setItems: function(items) {
        this.removeAll();
        //this.add(Ext.String.format('<b>{0}</b>', this.title));
        this.add(items);
    }
});
