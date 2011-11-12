Ext.define('devilry.administrator.period.Layout', {
    extend: 'Ext.container.Container',
    alias: 'widget.administrator-periodlayout',

    requires: [
        'devilry.administrator.period.PrettyView',
        'devilry.extjshelpers.RestfulSimplifiedEditPanel',
        'devilry.extjshelpers.forms.administrator.Period',
        'devilry.statistics.PeriodAdminLayout',
        'devilry.administrator.period.ListOfAssignments'
    ],
    
    config: {
        periodid: undefined
    },

    periodmodel_name: 'devilry.apps.administrator.simplified.SimplifiedPeriod',
    
    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
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
                    '<h1>{long_name}</h1>',
                    '<h2 class="endoflist">{parentnode__long_name}</h2>'
                ]
            }), {
                xtype: 'tabpanel',
                flex: 1,
                items: [
                {
                    xtype: 'administrator-period-listofassignments',
                    periodid: this.periodid,
                    title: 'Assignments'
                },
                //{
                    //title: 'Students',
                    //xtype: 'statistics-periodadminlayout',
                    //periodid: this.periodid,
                    //hidesidebar: false,
                    //defaultViewClsname: 'devilry.statistics.dataview.MinimalGridView'
                    ////defaultViewClsname: 'devilry.statistics.dataview.FullGridView'
                //},
                this.prettyview = Ext.widget('administrator_periodprettyview', {
                    title: 'Administer',
                    modelname: this.periodmodel_name,
                    objectid: this.periodid,
                    dashboardUrl: DASHBOARD_URL,
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
