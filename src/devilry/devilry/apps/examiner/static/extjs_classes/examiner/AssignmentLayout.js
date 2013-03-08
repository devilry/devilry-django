Ext.define('devilry.examiner.AssignmentLayout', {
    extend: 'Ext.container.Container',
    alias: 'widget.examiner-assignmentlayout',
    requires: [
        'devilry.examiner.AssignmentLayoutTodoList',
        'devilry.extjshelpers.SingleRecordContainer',
        'devilry.extjshelpers.SingleRecordView',
        'devilry_extjsextras.Router',
        'devilry.extjshelpers.studentsmanager.StudentsManager',
        'devilry_header.Breadcrumbs'
    ],
    cls: 'devilry_subtlebg',

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
        this.route = Ext.create('devilry_extjsextras.Router', this);
        this.route.add("", 'todo_route');
        this.route.add("students", 'students_route');

        var assignmentmodel = Ext.ModelManager.getModel(this.assignmentmodelname);
        assignmentmodel.load(this.assignmentid, {
            scope: this,
            success: this._onLoadAssignmentSuccess,
            failure: this._onLoadAssignmentFailure
        });

        this.heading = Ext.widget('singlerecordview', {
            singlerecordontainer: this.assignment_recordcontainer,
            margin: '20 0 0 0',
            tpl: Ext.create('Ext.XTemplate',
                '<div class="section pathheading bootstrap">',
                    '<h1 style="margin: 0; line-height: 25px;"><small>{parentnode__parentnode__short_name}.{parentnode__short_name}.</small>{long_name}</h1>',
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

    _init: function() {
        this.route.start();
    },

    todo_route: function() {
        var todo = this.down('examiner-assignmentlayout-todolist');
        if(todo !== null) { // Will be null for non-electronic
            todo.show();
        }
        this._setBreadcrumbsAndTitle();
    },
    students_route: function() {
        this.down('studentsmanager').show();
        this._setBreadcrumbsAndTitle(true);
    },

    _setBreadcrumbsAndTitle: function(students) {
        var record = this.assignmentRecord;
        var path = [
            record.get('parentnode__parentnode__short_name'),
            record.get('parentnode__short_name'),
            record.get('short_name')].join('.');
        var breadcrumbs = [];
        var active = path;
        if(students) {
            breadcrumbs.push({
                text: path,
                url: '#'
            });
            active = gettext('Students');
        }
        devilry_header.Breadcrumbs.getInBody().set(breadcrumbs, active);
        window.document.title = Ext.String.format('{0} - Devilry', path);
    },

    _onLoadAssignmentSuccess: function(record) {
        this.assignmentRecord = record;
        this.assignment_recordcontainer.setRecord(record);
    },

    _onLoadAssignmentFailure: function() {
        Ext.MessageBox.alert("Failed to load assignment. Please try to reload the page.");
    },

    _getStudentsManagerConfig: function() {
        return {
            xtype: 'studentsmanager',
            title: gettext('Detailed overview of all students'),
            assignmentgroupmodelname: this.assignmentgroupmodelname,
            assignmentid: this.assignmentid,
            assignmentrecord: this.assignment_recordcontainer.record,
            deadlinemodel: Ext.ModelManager.getModel('devilry.apps.examiner.simplified.SimplifiedDeadline'),
            gradeeditor_config_model: Ext.ModelManager.getModel('devilry.apps.gradeeditors.simplified.examiner.SimplifiedConfig'),
            isAdministrator: false,
            listeners: {
                scope: this,
                activate: function() {
                    this.route.navigate('#students');
                }
            }
        };
    },

    _getTodoListConfig: function() {
        return {
            xtype: 'examiner-assignmentlayout-todolist',
            assignmentid: this.assignmentid,
            pageSize: 30,
            assignmentmodelname: this.assignmentmodelname,
            assignmentgroupmodelname: this.assignmentgroupmodelname,
            listeners: {
                scope: this,
                activate: function() {
                    if(this.finishedLoading) {
                        this.route.navigate('');
                    }
                }
            }
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
        if(this.assignment_recordcontainer.record.get('delivery_types') === 1) {
            this._nonElectronicLayout();
        } else {
            this._electronicLayout();
        }
        this._init();
        this.finishedLoading = true;
        Ext.getBody().unmask();
    }
});
