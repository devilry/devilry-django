Ext.define('devilry.examiner.AssignmentLayout', {
    extend: 'Ext.container.Container',
    alias: 'widget.examiner-assignmentlayout',
    requires: [
        'devilry.examiner.AssignmentLayoutTodoList',
        'devilry.extjshelpers.SingleRecordContainer',
        'devilry.extjshelpers.SingleRecordView'
    ],
    
    config: {
        assignmentid: undefined,
        assignmentmodelname: undefined,
        assignmentgroupstore: undefined
    },
    
    constructor: function(config) {
        this.initConfig(config);
        this.assignment_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.assignment_recordcontainer.on('setRecord', this._onLoadRecord, this);
        this.callParent([config]);
    },
    
    initComponent: function() {
        this.heading = Ext.widget('singlerecordview', {
            singlerecordontainer: this.assignment_recordcontainer,
            tpl: Ext.create('Ext.XTemplate',
                '<div class="section treeheading">',
                '    <h1>{long_name} ({short_name})</h1>',
                '    <h2>{parentnode__long_name}</h2>',
                '    <h3>{parentnode__parentnode__long_name}</h3>',
                '</tpl>'
            ),
        });
        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [this.heading, {
                xtype: 'examiner-assignmentlayout-todolist',
                flex: 1,
                assignmentid: this.assignmentid,
                assignment_recordcontainer: this.assignment_recordcontainer,
                assignmentmodelname: this.assignmentmodelname,
                assignmentgroupstore: this.assignmentgroupstore
            }]
        });
        this.callParent(arguments);
    },

    _onLoadRecord: function() {
        Ext.getBody().unmask();
    }
});
