/**
 * A widget that shows if an assignment is anonymous, and provides an edit
 * button which a controller can use to handle changing the attribute.
 * */
Ext.define('devilry_subjectadmin.view.assignment.EditAnonymousWidget', {
    extend: 'Ext.container.Container',
    alias: 'widget.editanonymous-widget',
    cls: 'devilry_subjectadmin_editanonymous_widget',

    requires: [
        'devilry_subjectadmin.view.assignment.EditAnonymousPanel'
    ],

    initComponent: function() {
        Ext.apply(this, {
            layout: 'card',
            items: [{
                xtype: 'editablesidebarbox',
                itemId: 'readAnonymous',
                disabled: true,
                bodyTpl: '<p class="muted">{text}</p>'
            }, {
                xtype: 'editanonymouspanel',
                itemId: 'editAnonymous'
            }]
        });
        this.callParent(arguments);
    }
});
