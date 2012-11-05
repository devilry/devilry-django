Ext.define('devilry_subjectadmin.view.EditSidebarContainer', {
    extend: 'devilry_extjsextras.UnfocusedContainer',
    alias: 'widget.editsidebarcontainer',
    cls: 'devilry_subjectadmin_editsidebarcontainer',

    defaultOpacity: 0.8,
    hoverOpacity: 1,

    mouseEnterExtras: function() {
        this.getEl().setStyle('background-color', '#fff');  
    },
    mouseLeaveExtras: function() {
        this.getEl().setStyle('background-color', 'transparent');  
    }
});
