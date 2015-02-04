Ext.define('devilry_subjectadmin.view.EditSidebarContainer', {
    extend: 'devilry_extjsextras.UnfocusedContainer',
    alias: 'widget.editsidebarcontainer',
    cls: 'devilry_subjectadmin_editsidebarcontainer',

    defaultOpacity: 1,
    hoverOpacity: 1,

    mouseEnterExtras: function() {
        //this.getEl().setStyle('background-color', '#fff');
        this.getEl().addCls('devilry_subjectadmin_editsidebarcontainer_hover');
    },
    mouseLeaveExtras: function() {
        this.getEl().removeCls('devilry_subjectadmin_editsidebarcontainer_hover');
        //this.getEl().setStyle('background-color', 'transparent');
    }
});
