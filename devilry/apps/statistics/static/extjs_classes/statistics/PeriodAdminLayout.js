Ext.define('devilry.statistics.PeriodAdminLayout', {
    extend: 'Ext.container.Container',
    alias: 'widget.statistics-periodadminlayout', // NOTE: devilry.statistics.sidebarplugin.qualifiesforexam.Manual depends on this alias
    layout: 'fit',
    requires: [
        'devilry.statistics.Loader',
        'devilry.statistics.LabelConfig',
        'devilry.statistics.FilterEditor',
        'devilry.statistics.LabelOverview',
        'devilry.statistics.LabelConfigEditor',
        'devilry.statistics.SidebarPluginContainer',
        'devilry.statistics.dataview.DataView',
        'devilry.statistics.sidebarplugin.qualifiesforexam.Main'
    ],

    config: {
        periodid: undefined,

        sidebarplugins: [
            'devilry.statistics.sidebarplugin.qualifiesforexam.Main'
        ]
    },

    titleTpl: Ext.create('Ext.XTemplate',
        '{parentnode__long_name:ellipsis(60)} &mdash; {long_name}'
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
                loaded: this._onLoaded
            }
        });
    },

    _onLoaded: function(loader) {
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
                width: 300,
                autoScroll: true,
                loader: loader,
                sidebarplugins: this.sidebarplugins
            }, this._dataview = Ext.widget('statistics-dataview', {
                //flex: 7,
                region: 'center',
                loader: loader
            })]
        });
    }
});
