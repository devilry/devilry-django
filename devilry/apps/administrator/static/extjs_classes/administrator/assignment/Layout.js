Ext.define('devilry.administrator.assignment.Layout', {
    extend: 'Ext.container.Container',
    alias: 'widget.administrator-assignmentlayout',

    requires: [
        'devilry.administrator.assignment.PrettyView',
        'devilry.extjshelpers.RestfulSimplifiedEditPanel',
        'devilry.extjshelpers.forms.administrator.Assignment'
    ],

    /**
     * @cfg
     */
    assignmentid: undefined,

    /**
     * @cfg
     */
    assignmentgroupstore: undefined,

    assignmentmodel_name: 'devilry.apps.administrator.simplified.SimplifiedAssignment',
    
    initComponent: function() {
        var query = Ext.Object.fromQueryString(window.location.search);
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
                    '<h1>{long_name}</h1>',
                    '<h2>{parentnode__long_name}</h2>',
                    '<h3 class="endoflist">{parentnode__parentnode__long_name}</h2>'
                ]
            }), {
                xtype: 'tabpanel',
                flex: 1,
                activeTab: query.open_students == 'yes'? 1: 0,
                items: [this.prettyview = Ext.widget('administrator_assignmentprettyview', {
                    title: 'Administer',
                    modelname: this.assignmentmodel_name,
                    objectid: this.assignmentid,
                    dashboardUrl: DASHBOARD_URL,
                    assignmentgroupstore: this.assignmentgroupstore,
                    listeners: {
                        scope: this,
                        loadmodel: this._onLoadRecord,
                        edit: this._onEdit
                    }
                })]
            }]
        });
        this.callParent(arguments);
    },

    _onLoadRecord: function(record) {
        this.heading.update(record.data);
    },

    _onEdit: function(record, button) {
        var editpanel = Ext.ComponentManager.create({
            xtype: 'restfulsimplified_editpanel',
            model: this.periodmodel_name,
            editform: Ext.widget('administrator_periodform'),
            record: record
        });
        var editwindow = Ext.create('devilry.administrator.DefaultEditWindow', {
            editpanel: editpanel,
            prettyview: this.prettyview
        });
        editwindow.show();
    }
});
