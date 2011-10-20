Ext.define('devilry.statistics.PeriodAdminLayout', {
    extend: 'Ext.container.Viewport',
    layout: 'border',
    requires: [
        'devilry.statistics.Loader',
        'devilry.statistics.LabelConfig',
        'devilry.statistics.FilterEditor',
        'devilry.statistics.LabelOverview',
        'devilry.statistics.LabelConfigEditor',
        'devilry.statistics.SidebarPluginContainer',
        'devilry.statistics.sidebarplugin.qualifiesforexam.Main'
    ],

    config: {
        periodid: undefined,
        sidebarplugins: [
            'devilry.statistics.sidebarplugin.qualifiesforexam.Main'
        ]
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
    initComponent: function() {
        Ext.apply(this, {
            style: 'background-color: transparent',
            items: [{
                region: 'north',
                xtype: 'pageheader',
                navclass: 'administrator'
            }, {
                region: 'south',
                xtype: 'pagefooter'
            }, this._center = Ext.widget('panel', {
                region: 'center',
                layout: {
                    type: 'hbox',
                    align: 'stretch'
                },
                padding: {left: 20, right: 20}
            })]
        });
        this.callParent(arguments);
        this._loadStudents();
    },

    _loadStudents: function() {
        Ext.getBody().mask("Loading page", 'page-load-mask');
        Ext.create('devilry.statistics.Loader', this.periodid, {
            listeners: {
                scope: this,
                loaded: this._onLoaded,
                datachange: this._onDatachange
            }
        });
    },

    _onDatachange: function(extjsStructures) {
        this.aggregatedStore.removeAll();
        this.aggregatedStore.add(extjsStructures.storeStudents);
        //this.aggregatedStore.loadRecords(extjsStructures.storeStudents);
    },

    _onLoaded: function(loader) {
        var extjsStructures = loader.extjsFormat();
        Ext.getBody().unmask();

        this.aggregatedStore = Ext.create('Ext.data.Store', {
            fields: extjsStructures.storeFields,
            data: {'items': []},
            proxy: {
                type: 'memory',
                reader: {
                    type: 'json',
                    root: 'items'
                }
            }
        });
        this._onDatachange(extjsStructures);

        //var qualifiesForExam = Ext.create('devilry.statistics.LabelConfig', {
            //label: 'qualifies-for-exam'
        //});
        //qualifiesForExam.addFilter({
            //must_pass: [
                //[loader.getAssignmentByShortName('week1').get('id'), loader.getAssignmentByShortName('week3').get('id')],
                //[loader.getAssignmentByShortName('week2').get('id')]
            //],
            //pointspec: Ext.create('devilry.statistics.PointSpec', {
                //assignments: [
                    //[loader.getAssignmentByShortName('week2').get('id'), loader.getAssignmentByShortName('week3').get('id')],
                    //[loader.getAssignmentByShortName('week1').get('id')]
                //],
                //min: 10,
                //max: 40
            //})
        //});


        this._center.add([{
            xtype: 'statistics-sidebarplugincontainer',
            flex: 3,
            autoScroll: true,
            loader: loader,
            aggregatedStore: this.aggregatedStore,
            sidebarplugins: this.sidebarplugins
        }, {
            xtype: 'grid',
            title: 'Details',
            autoScroll: true,
            flex: 7,
            store: this.aggregatedStore,
            columns: extjsStructures.gridColumns,
        }]);


        //this.aggregatedStore.filter(
            //Ext.create('Ext.util.Filter', {
                //filterFn: function(item) {
                    //var username = item.get('username');
                    //var student = loader.getStudentByName(username);
                    //var m = approvedFilter.match(loader, student);
                    //return m;
                //}
            //})
        //);
    }
});
