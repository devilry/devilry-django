Ext.define('devilry.administrator.assignment.Layout', {
    extend: 'Ext.container.Container',
    alias: 'widget.administrator-assignmentlayout',

    requires: [
        'devilry.administrator.assignment.PrettyView',
        'devilry.extjshelpers.RestfulSimplifiedEditPanel',
        'devilry.extjshelpers.forms.administrator.Assignment',
        'devilry_header.Breadcrumbs',
        'devilry_extjsextras.Router',
        'devilry_header.Breadcrumbs'
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
        this.route = Ext.create('devilry_extjsextras.Router', this);
        this.route.add("", 'administer_route');
        this.route.add("students", 'students_route');
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
                activeTab: window.location.hash == '#students'? 1: 0,
                items: [this.prettyview = Ext.widget('administrator_assignmentprettyview', {
                    title: gettext('Administer'),
                    itemId: 'administer',
                    modelname: this.assignmentmodel_name,
                    objectid: this.assignmentid,
                    dashboardUrl: this.dashboardUrl,
                    assignmentgroupmodelname: this.assignmentgroupmodelname,
                    listeners: {
                        scope: this,
                        loadmodel: this._onLoadRecord,
                        loadmodelFailed: this._onLoadRecordFailed,
                        edit: this._onEdit,
                        activate: function() {
                            this.route.navigate('');
                            if(this.prettyview.record) {
                                this.prettyview.checkStudentsAndRefreshBody();
                            }
                        }
                    }
                }), this.studentstab = Ext.widget('panel', {
                    title: gettext('Students'),
                    itemId: 'students',
                    layout: 'fit',
                    listeners: {
                        scope: this,
                        activate: function() {
                            this.route.navigate('students');
                        }
                    }
                })]
            }]
        });
        this.callParent(arguments);
    },

    _starteRouting: function() {
        if(!this.route_started) {
            this.route_started = true;
            this.route.start();
        }
    },

    administer_route: function() {
        this.down('#administer').show();
        this._setBreadcrumbAndTitle();
    },
    students_route: function() {
        this.down('#students').show();
        this._setBreadcrumbAndTitle(true);
    },

    _onLoadRecord: function(assignmentRecord) {
        this.assignmentRecord = assignmentRecord;
        this.heading.update({
            hasdata: true,
            assignment: assignmentRecord.data,
            DEVILRY_URLPATH_PREFIX: DevilrySettings.DEVILRY_URLPATH_PREFIX
        });
        this._onStudents();
        this._starteRouting();
    },

    _onLoadRecordFailed: function(operation) {
        this.removeAll();
        var title = operation.error.statusText;
        if(operation.error.status == '403') {
            title = gettext('Permission denied');
            message = gettext('You are not administrator on this item or any of its parents.');
        }
        this.add({
            xtype: 'box',
            padding: 20,
            tpl: [
                '<div class="section warning">',
                    '<h2>{title}</h2>',
                    '<p>{message}</p>',
                '</div>'
            ],
            data: {
                title: title,
                message: message
            }
        });
    },

    _setBreadcrumbAndTitle: function(students) {
        var assignmentRecord = this.assignmentRecord;
        var path = [
            assignmentRecord.get('parentnode__parentnode__short_name'),
            assignmentRecord.get('parentnode__short_name'),
            assignmentRecord.get('short_name')].join('.');
        window.document.title = Ext.String.format('{0} - Devilry', path);
        var breadcrumbs = [{
            text: assignmentRecord.get('parentnode__parentnode__short_name'),
            url: '../subject/' + assignmentRecord.get('parentnode__parentnode')
        }, {
            text: assignmentRecord.get('parentnode__short_name'),
            url: '../period/' + assignmentRecord.get('parentnode')
        }];
        var active = assignmentRecord.get('short_name');
        if(students) {
            breadcrumbs.push({
                text: assignmentRecord.get('short_name'),
                url: '#'
            });
            active = gettext('Students')
        }
        devilry_header.Breadcrumbs.getInBody().set(breadcrumbs, active);
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
