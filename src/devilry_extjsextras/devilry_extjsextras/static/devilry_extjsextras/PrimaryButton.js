/**
Button intended as the primary button in a view (the one it is most natural to
click by default).
*/ 
Ext.define('devilry_extjsextras.PrimaryButton', {
    extend: 'Ext.button.Button',
    alias: 'widget.primarybutton',
    cls: 'devilry_primarybutton',
    scale: 'large',
    //minWidth: 150,
    ui: 'primary'
});
