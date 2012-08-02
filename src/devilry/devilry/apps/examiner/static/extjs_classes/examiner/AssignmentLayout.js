Ext.define('devilry.examiner.AssignmentLayout', {
    extend: 'Ext.container.Container',
    alias: 'widget.examiner-assignmentlayout',
    requires: [
        'devilry.examiner.AssignmentLayoutTodoList',
        'devilry.extjshelpers.SingleRecordContainer',
        'devilry.extjshelpers.SingleRecordView',
        'devilry_header.Breadcrumbs'
    ],
    
    /**
     * @cfg
     */
    assignmentid: undefined,
    

    assignmentmodelname: 'devilry.apps.examiner.simplified.SimplifiedAssignment',
    assignmentgroupmodelname: 'devilry.apps.examiner.simplified.SimplifiedAssignmentGroup',
    
    constructor: function(config) {
        this.assignment_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.assignment_recordcontainer.on('setRecord', this._onLoadRecord, this);
        this.callParent(arguments);
    },
    
    initComponent: function() {
        var assignmentmodel = Ext.ModelManager.getModel(this.assignmentmodelname);
        assignmentmodel.load(this.assignmentid, {
            scope: this,
            success: this._onLoadAssignmentSuccess,
            failure: this._onLoadAssignmentFailure
        });

        this.heading = Ext.widget('singlerecordview', {
            singlerecordontainer: this.assignment_recordcontainer,
            tpl: Ext.create('Ext.XTemplate',
                '<div class="section pathheading">',
                '    <h1><small>{parentnode__parentnode__short_name}.{parentnode__short_name}.</small>{long_name}</h1>',
                '</div>'
            )
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
        var path = [
            record.get('parentnode__parentnode__short_name'),
            record.get('parentnode__short_name'),
            record.get('short_name')].join('.');
        devilry_header.Breadcrumbs.getInBody().set([], path);
        window.document.title = Ext.String.format('{0} - Devilry', path);
    },

    _onLoadAssignmentFailure: function() {
        Ext.MessageBox.alert("Failed to load assignment. Please try to reload the page.");
    },

    _getStudentsManagerConfig: function() {
        return {
            xtype: 'studentsmanager',
            title: 'Detailed overview of all students',
            assignmentgroupmodelname: this.assignmentgroupmodelname,
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
            pageSize: 30,
            assignmentmodelname: this.assignmentmodelname,
            assignmentgroupmodelname: this.assignmentgroupmodelname
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
