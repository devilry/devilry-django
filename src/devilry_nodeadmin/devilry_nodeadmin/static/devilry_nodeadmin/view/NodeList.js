Ext.define('devilry_nodeadmin.view.NodeList' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.nodeadmin.nodelist',
    cls: 'devilry_nodeadmin_nodelist',
    requires: [
        'Ext.layout.container.Column',
        'devilry_extjsextras.EditableSidebarBox',
        'devilry_extjsextras.AlertMessageList'
    ],

    initComponent: function() {

    }
});