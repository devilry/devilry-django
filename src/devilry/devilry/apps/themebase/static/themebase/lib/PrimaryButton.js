/**
Button intended as the primary button in a view (the one it is most natural to
click by default).
*/ 
Ext.define('themebase.PrimaryButton', {
    extend: 'Ext.button.Button',
    alias: 'widget.primarybutton',
    cls: 'primarybutton',
    scale: 'large',
    ui: 'primary'
});
