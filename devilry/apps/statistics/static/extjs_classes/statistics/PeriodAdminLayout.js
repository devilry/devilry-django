Ext.define('devilry.statistics.PeriodAdminLayout', {
    extend: 'Ext.container.Viewport',
    layout: 'border',
    requires: [
        'devilry.statistics.Loader',
        'devilry.statistics.LabelConfig',
        'devilry.statistics.FilterEditor'
    ],

    config: {
        periodid: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
    initComponent: function() {
        //this._center = Ext.widget('container', {
            //region: 'center',
            //layout: 'fit'
        //});
        Ext.apply(this, {
            style: 'background-color: transparent',
            items: [{
                region: 'north',
                xtype: 'pageheader',
                navclass: 'administrator'
            }, {
                region: 'south',
                xtype: 'pagefooter'
            }, this._center = Ext.widget('container', {
                region: 'center',
                style: 'background-color: transparent',
                layout: {
                    type: 'hbox',
                    align: 'stretch'
                },
                padding: {left: 20, right: 20}
                //items: [this._center, {
                    //xtype: 'statistics-filtereditor',
                    //region: 'east',
                    //title: 'Configurable labels',
                    //width: 300,
                    //collapsible: true,
                //}]
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
                loaded: this._onLoaded
            }
        });
    },

    _onLoaded: function(loader) {
        var extjsStructures = loader.extjsFormat();
        Ext.getBody().unmask();

        var store = Ext.create('Ext.data.Store', {
            fields: extjsStructures.storeFields,
            data: {'items': extjsStructures.storeStudents},
            proxy: {
                type: 'memory',
                reader: {
                    type: 'json',
                    root: 'items'
                }
            }
        });

        this._center.add([{
            xtype: 'grid',
            autoScroll: true,
            flex: 1,
            store: store,
            columns: extjsStructures.gridColumns,
        }, {
            xtype: 'statistics-filtereditor',
            region: 'east',
            title: 'Configurable labels',
            assignment_store: loader.assignment_store,
            width: 300
        }])


        //var approvedFilter = Ext.create('devilry.statistics.LabelConfig', {
            //label: 'Approved'
        //});
        //approvedFilter.addFilter({
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
        //store.filter(
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
