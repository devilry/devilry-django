/**
Delete button
*/ 
Ext.define('devilry_extjsextras.DeleteButton', {
    extend: 'Ext.button.Button',
    alias: 'widget.deletebutton',
    scale: 'large',
    cls: 'devilry_deletebutton',
    text: pgettext('uibutton', 'Delete')
});
