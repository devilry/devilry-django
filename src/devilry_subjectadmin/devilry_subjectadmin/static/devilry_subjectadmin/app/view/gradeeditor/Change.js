Ext.define('devilry_subjectadmin.view.gradeeditor.Change' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.gradeeditorchange',
    cls: 'devilry_subjectadmin_gradeeditorchange',

    initComponent: function() {
        Ext.apply(this, {
            layout: 'column',
            items: [{
                xtype: 'box',
                width: 300,
                cls: 'bootstrap',
                html: [
                    '<h2>', gettext('Select a grade editor'), '</h2>'
                ].join('')
            }]
        });
        this.callParent(arguments);
    }
});
