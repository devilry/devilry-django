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
                cls: 'section pathheading',
                tpl: [
                    '<tpl if="!hasdata">',
                    '   <span class="loading">Loading...</span>',
                    '</tpl>',
                    '<tpl if="hasdata">',
                    '    <h1><small>{assignment.parentnode__parentnode__short_name}.{assignment.parentnode__short_name}.</small>{assignment.long_name}</h1>',
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
        this._setBreadcrumbAndTitle(assignmentRecord);
    },

    _setBreadcrumbAndTitle: function(assignmentRecord) {
        var path = [
            assignmentRecord.get('parentnode__parentnode__short_name'),
            assignmentRecord.get('parentnode__short_name'),
            assignmentRecord.get('short_name')].join('.');
        window.document.title = Ext.String.format('{0} - Devilry', path);
        devilry_header.Breadcrumbs.getInBody().set([{
            text: assignmentRecord.get('parentnode__parentnode__short_name'),
            url: '../subject/' + assignmentRecord.get('parentnode__parentnode')
        }, {
            text: assignmentRecord.get('parentnode__short_name'),
            url: '../period/' + assignmentRecord.get('parentnode')
        }], assignmentRecord.get('short_name'));
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
