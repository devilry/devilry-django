Ext.define('devilry.administrator.node.Layout', {
    extend: 'Ext.container.Container',
    alias: 'widget.administrator-nodelayout',

    requires: [
        'devilry.administrator.node.PrettyView',
        'devilry.extjshelpers.RestfulSimplifiedEditPanel',
        'devilry.extjshelpers.forms.administrator.Node',
        'devilry.administrator.ListOfChildnodes'
    ],
    
    /**
     * @cfg
     */
    nodeid: undefined,

    nodemodel_name: 'devilry.apps.administrator.simplified.SimplifiedNode',
    
    initComponent: function() {
        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [this.heading = Ext.ComponentManager.create({
                xtype: 'component',
                data: {},
                cls: 'section treeheading',
                tpl: [
                    '<tpl if="!hasdata">',
                    '   <span class="loading">Loading...</span>',
                    '</tpl>',
                    '<tpl if="hasdata">',
                    '    <h1 class="endoflist">',
                    '       {node.long_name}',
                    '    </h1>',
                    '</tpl>'
                ]
            }), {
                xtype: 'tabpanel',
                flex: 1,
                items: [this.prettyview = Ext.widget('administrator_nodeprettyview', {
                    title: 'Administer',
                    modelname: this.nodemodel_name,
                    objectid: this.nodeid,
                    dashboardUrl: DASHBOARD_URL,
                    listeners: {
                        scope: this,
                        loadmodel: this._onLoadRecord,
                        edit: this._onEdit
                    }
                }), {
                    xtype: 'administrator-listofchildnodes',
                    title: 'Direct childnodes',
                    parentnodeid: this.nodeid,
                    orderby: 'short_name',
                    modelname: 'devilry.apps.administrator.simplified.SimplifiedNodeList',
                    urlrolepart: 'node'
                }, {
                    xtype: 'administrator-listofchildnodes',
                    title: 'Subjects',
                    parentnodeid: this.nodeid,
                    orderby: 'short_name',
                    modelname: 'devilry.apps.administrator.simplified.SimplifiedSubjectList',
                    urlrolepart: 'subject'
                }]
            }]
        });
        this.callParent(arguments);
    },

    _onLoadRecord: function(nodeRecord) {
        this.heading.update({
            hasdata: true,
            node: nodeRecord.data
        });
    },

    _onEdit: function(record, button) {
        var editpanel = Ext.ComponentManager.create({
            xtype: 'restfulsimplified_editpanel',
            model: this.nodemodel_name,
            editform: Ext.widget('administrator_nodeform'),
            record: record
        });
        var editwindow = Ext.create('devilry.administrator.DefaultEditWindow', {
            editpanel: editpanel,
            prettyview: this.prettyview
        });
        editwindow.show();
    }
});
