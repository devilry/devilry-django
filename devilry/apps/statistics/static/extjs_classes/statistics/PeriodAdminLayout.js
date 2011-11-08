Ext.define('devilry.statistics.PeriodAdminLayout', {
    extend: 'Ext.container.Container',
    alias: 'widget.statistics-periodadminlayout', // NOTE: devilry.statistics.sidebarplugin.qualifiesforexam.Manual depends on this alias
    layout: 'fit',
    requires: [
        'devilry.statistics.Loader',
        'devilry.statistics.SidebarPluginContainer',
        'devilry.statistics.dataview.DataView',
        'devilry.statistics.sidebarplugin.qualifiesforexam.Main',
        'devilry.statistics.OverviewOfSingleStudent'
    ],

    config: {
        periodid: undefined,
        defaultViewClsname: 'devilry.statistics.dataview.FullGridView',
        hidesidebar: false,

        sidebarplugins: [
            'devilry.statistics.sidebarplugin.qualifiesforexam.Main'
        ]
    },

    titleTpl: Ext.create('Ext.XTemplate',
        '{parentnode__long_name:ellipsis(60)} &mdash; {long_name}'
    ),

    selectedStudentTitleTpl: Ext.create('Ext.XTemplate',
        '{full_name} ({username})'
    ),

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
    initComponent: function() {
        Ext.apply(this, {
            style: 'background-color: transparent',
            items: []
        });
        this.callParent(arguments);
        this._loadStudents();
    },

    _loadStudents: function() {
        Ext.getBody().mask("Loading page", 'page-load-mask');
        Ext.create('devilry.statistics.Loader', this.periodid, {
            listeners: {
                scope: this,
                minimalDatasetLoaded: this._onMinimalDatasetLoaded
            }
        });
    },

    _onMinimalDatasetLoaded: function(loader) {
        Ext.getBody().unmask();

        var title = this.titleTpl.apply(loader.periodRecord.data);
        this.up('window').setTitle(title);
            
        this.add({
            xtype: 'panel',
            layout: 'border',
            items: [{
                xtype: 'statistics-sidebarplugincontainer',
                //flex: 3,
                title: 'Label students',
                region: 'east',
                collapsible: true,
                collapsed: this.hidesidebar,
                width: 300,
                autoScroll: true,
                loader: loader,
                sidebarplugins: this.sidebarplugins
            }, this._dataview = Ext.widget('statistics-dataview', {
                //flex: 7,
                defaultViewClsname: this.defaultViewClsname,
                region: 'center',
                loader: loader,
                listeners: {
                    scope: this,
                    selectStudent: this._onSelectStudent
                }
            }), this._detailsPanel = Ext.widget('panel', {
                title: 'Select a student to view their details',
                region: 'south',
                autoScroll: true,
                layout: 'fit',
                height: 200,
                collapsed: true,
                collapsible: true
            })]
        });
    },

    _onSelectStudent: function(record) {
        this._detailsPanel.removeAll();
        this._detailsPanel.expand();
        var assignmentgroups = [];
        Ext.Object.each(record.groupsByAssignmentId, function(assignmentid, group) {
            if(group.assignmentGroupRecord != null) {
                assignmentgroups.push(group.assignmentGroupRecord.data);
            }
        }, this);
        this._detailsPanel.setTitle(this.selectedStudentTitleTpl.apply(record.data));
        this._detailsPanel.add({
            xtype: 'statistics-overviewofsinglestudent',
            assignment_store: record.assignment_store,
            assignmentgroups: assignmentgroups,
            username: record.get('username'),
            full_name: record.get('full_name'),
            labelKeys: record.get('labelKeys'),
            border: false,
            frame: false
        });
    }
});
