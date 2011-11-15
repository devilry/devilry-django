Ext.define('devilry.examiner.AssignmentLayout', {
    extend: 'Ext.container.Container',
    alias: 'widget.examiner-assignmentlayout',
    requires: [
        'devilry.examiner.AssignmentLayoutTodoList',
        'devilry.extjshelpers.SingleRecordContainer',
        'devilry.extjshelpers.SingleRecordView'
    ],
    
    /**
     * @cfg
     */
    assignmentid: undefined,
    
    /**
     * @cfg
     */
    assignmentmodelname: undefined,
    
    /**
     * @cfg
     */
    assignmentgroupstore: undefined,
    
    /**
     * @cfg
     */
    assignmentmodelname_todolist: undefined,
    
    constructor: function(config) {
        this.assignment_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.assignment_recordcontainer.on('setRecord', this._onLoadRecord, this);
        this.callParent(arguments);
    },
    
    initComponent: function() {
        this.todostore = Ext.create('Ext.data.Store', {
            model: this.assignmentmodelname_todolist,
            remoteFilter: true,
            remoteSort: true
        });
        var assignmentmodel = Ext.ModelManager.getModel(this.assignmentmodelname);
        assignmentmodel.load(this.assignmentid, {
            scope: this,
            success: this._onLoadAssignmentSuccess,
            failure: this._onLoadAssignmentFailure
        });

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
            items: []
        });
        this.callParent(arguments);
    },

    _onLoadAssignmentSuccess: function(record) {
        this.assignment_recordcontainer.setRecord(record);
    },

    _onLoadAssignmentFailure: function() {
        Ext.MessageBox.alert("Failed to load assignment. Please try to reload the page.");
    },

    _getStudentsManagerConfig: function() {
        return {
            xtype: 'studentsmanager',
            title: 'Detailed overview of all students',
            assignmentgroupstore: this.assignmentgroupstore,
            assignmentid: this.assignmentid,
            assignmentrecord: this.assignment_recordcontainer.record,
            deadlinemodel: Ext.ModelManager.getModel('devilry.apps.examiner.simplified.SimplifiedDeadline'),
            gradeeditor_config_model: Ext.ModelManager.getModel('devilry.apps.gradeeditors.simplified.examiner.SimplifiedConfig'),
            isAdministrator: false
        };
    },

    _getTodoListConfig: function() {
        return {
            xtype: 'examiner-assignmentlayout-todolist',
            assignmentid: this.assignmentid,
            assignment_recordcontainer: this.assignment_recordcontainer,
            assignmentmodelname: this.assignmentmodelname_todolist,
            assignmentgroupstore: this.todostore
        };
    },

    _electronicLayout: function() {
        this.add([this.heading, {
            xtype: 'tabpanel',
            flex: 1,
            items: [this._getTodoListConfig(), this._getStudentsManagerConfig()]
        }]);
    },

    _nonElectronicLayout: function() {
        var studentsmanagerConf = this._getStudentsManagerConfig();
        studentsmanagerConf.flex = 1;
        this.add([this.heading, studentsmanagerConf]);
    },

    _onLoadRecord: function() {
        if(this.assignment_recordcontainer.record.get('delivery_types') == 1) {
            this._nonElectronicLayout();
        } else {
            this._electronicLayout();
        }
        Ext.getBody().unmask();
    },
});
