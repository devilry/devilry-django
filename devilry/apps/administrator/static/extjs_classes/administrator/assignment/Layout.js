Ext.define('devilry.administrator.assignment.Layout', {
    extend: 'Ext.container.Container',
    alias: 'widget.administrator-assignmentlayout',

    requires: [
        'devilry.administrator.assignment.PrettyView',
        'devilry.extjshelpers.RestfulSimplifiedEditPanel',
        'devilry.extjshelpers.forms.administrator.Assignment'
    ],

    /**
     * @cfg
     */
    assignmentid: undefined,

    /**
     * @cfg
     */
    dashboardUrl: undefined,

    assignmentmodel_name: 'devilry.apps.administrator.simplified.SimplifiedAssignment',
    assignmentgroupmodelname: 'devilry.apps.administrator.simplified.SimplifiedAssignmentGroup',
    
    initComponent: function() {
        this.studentsLoaded = false;
        var query = Ext.Object.fromQueryString(window.location.search);
        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [this.heading = Ext.ComponentManager.create({
                xtype: 'component',
                data: {hasdata: false},
                cls: 'section treeheading',
                tpl: [
                    '<tpl if="!hasdata">',
                    '   <span class="loading">Loading...</span>',
                    '</tpl>',
                    '<tpl if="hasdata">',
                    '    <h1>{assignment.long_name}</h1>',
                    '    <h2><a href="{DEVILRY_URLPATH_PREFIX}/administrator/period/{assignment.parentnode}">',
                    '       {assignment.parentnode__long_name}',
                    '    </a></h2>',
                    '    <h3 class="endoflist"><a href="{DEVILRY_URLPATH_PREFIX}/administrator/subject/{assignment.parentnode__parentnode}">',
                    '       {assignment.parentnode__parentnode__long_name}',
                    '    </a></h2>',
                    '</tpl>'
                ]
            }), {
                xtype: 'tabpanel',
                flex: 1,
                activeTab: query.open_students == 'yes'? 1: 0,
                items: [this.prettyview = Ext.widget('administrator_assignmentprettyview', {
                    title: 'Administer',
                    modelname: this.assignmentmodel_name,
                    objectid: this.assignmentid,
                    dashboardUrl: this.dashboardUrl,
                    assignmentgroupmodelname: this.assignmentgroupmodelname,
                    listeners: {
                        scope: this,
                        loadmodel: this._onLoadRecord,
                        edit: this._onEdit,
                        activate: function() {
                            if(this.prettyview.record) {
                                this.prettyview.checkStudentsAndRefreshBody();
                            }
                        }
                    }
                }), this.studentstab = Ext.widget('panel', {
                    title: 'Students',
                    layout: 'fit'
                })]
            }]
        });
        this.callParent(arguments);
    },

    _onLoadRecord: function(assignmentRecord) {
        this.assignmentRecord = assignmentRecord;
        this.heading.update({
            hasdata: true,
            assignment: assignmentRecord.data,
            DEVILRY_URLPATH_PREFIX: DevilrySettings.DEVILRY_URLPATH_PREFIX
        });
        this._onStudents();
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
    },


    _onStudents: function() {
        if(this.studentsLoaded) {
            return;
        }
        this.studentsLoaded = true;
        this.studentstab.add({
            xtype: 'administrator_studentsmanager',
            assignmentid: this.assignmentid,
            assignmentrecord: this.assignmentRecord,
            periodid: this.assignmentRecord.data.parentnode,
            deadlinemodel: Ext.ModelManager.getModel('devilry.apps.administrator.simplified.SimplifiedDeadline'),
            gradeeditor_config_model: Ext.ModelManager.getModel('devilry.apps.gradeeditors.simplified.administrator.SimplifiedConfig'),
            assignmentgroupmodelname: this.assignmentgroupmodelname,
            isAdministrator: true
        });
    }
});
