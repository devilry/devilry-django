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
    assignmentgroupstore: undefined,

    assignmentmodel_name: 'devilry.apps.administrator.simplified.SimplifiedAssignment',
    
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
                data: {},
                cls: 'section treeheading',
                tpl: [
                    '<h1>{long_name}</h1>',
                    '<h2>{parentnode__long_name}</h2>',
                    '<h3 class="endoflist">{parentnode__parentnode__long_name}</h2>'
                ]
            }), {
                xtype: 'tabpanel',
                flex: 1,
                activeTab: query.open_students == 'yes'? 1: 0,
                items: [this.prettyview = Ext.widget('administrator_assignmentprettyview', {
                    title: 'Administer',
                    modelname: this.assignmentmodel_name,
                    objectid: this.assignmentid,
                    dashboardUrl: DASHBOARD_URL,
                    assignmentgroupstore: this.assignmentgroupstore,
                    listeners: {
                        scope: this,
                        loadmodel: this._onLoadRecord,
                        edit: this._onEdit,
                        activate: function() {
                            if(this.prettyview.record) {
                                this.prettyview.refreshBody();
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
        this.heading.update(assignmentRecord.data);
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
            assignmentgroupstore: this.assignmentgroupstore,
            assignmentid: this.assignmentid,
            assignmentrecord: this.assignmentRecord,
            periodid: this.assignmentRecord.data.parentnode,
            deadlinemodel: Ext.ModelManager.getModel('devilry.apps.administrator.simplified.SimplifiedDeadline'),
            gradeeditor_config_model: Ext.ModelManager.getModel('devilry.apps.gradeeditors.simplified.administrator.SimplifiedConfig'),
            isAdministrator: true
        });
    }
});
