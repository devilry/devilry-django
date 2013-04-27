Ext.define('devilry_student.view.browse.Browse' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.browse',
    cls: 'devilry_student_browse',

    layout: 'card',
    items: [{
        xtype: 'browselist',
        itemId: 'list'
    }, {
        xtype: 'browsecalendar',
        itemId: 'calendar'
    }]
});
