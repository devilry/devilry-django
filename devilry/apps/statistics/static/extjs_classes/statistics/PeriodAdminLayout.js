Ext.define('devilry.statistics.PeriodAdminLayout', {
    extend: 'Ext.container.Viewport',
    layout: 'border',
    style: 'background-color: transparent',
    requires: [
        'devilry.statistics.Loader',
        'devilry.statistics.FilterGroup'
    ],

    config: {
        periodid: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
    initComponent: function() {
        Ext.apply(this, {
            items: [//{
                //region: 'north',
                //xtype: 'pageheader',
                //navclass: 'administrator'
            //}, {
                //region: 'south',
                //xtype: 'pagefooter'
            //}, 
            this._center = Ext.widget('container', {
                region: 'center',
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

        this._center.add({
            xtype: 'grid',
            store: store,
            columns: extjsStructures.gridColumns,
        });

        var approvedFilter = Ext.create('devilry.statistics.FilterGroup', {
            title: 'Approved'
        });
        approvedFilter.addFilter({
            must_pass: [
                [loader.getAssignmentByShortName('week1').get('id'), loader.getAssignmentByShortName('week3').get('id')],
                [loader.getAssignmentByShortName('week2').get('id')]
            ],
            pointspec: Ext.create('devilry.statistics.PointSpec', {
                assignments: [
                    [loader.getAssignmentByShortName('week2').get('id'), loader.getAssignmentByShortName('week3').get('id')],
                    [loader.getAssignmentByShortName('week1').get('id')]
                ],
                min: 10,
                max: 40
            })
        });
        store.filter(
            Ext.create('Ext.util.Filter', {
                filterFn: function(item) {
                    var username = item.get('username');
                    var student = loader.getStudentByName(username);
                    var m = approvedFilter.match(loader, student);
                    return m;
                }
            })
        );
    }
});
