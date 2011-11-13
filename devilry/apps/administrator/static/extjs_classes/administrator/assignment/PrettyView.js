/** PrettyView for an assignment. */
Ext.define('devilry.administrator.assignment.PrettyView', {
    extend: 'devilry.administrator.PrettyView',
    alias: 'widget.administrator_assignmentprettyview',
    requires: [
        'devilry.administrator.studentsmanager.StudentsManager',
        'devilry.extjshelpers.RestfulSimplifiedEditPanel',
        'devilry.extjshelpers.SingleRecordContainer',
        'devilry.extjshelpers.MaximizableWindow',
        'devilry.gradeeditors.GradeEditorModel',
        'devilry.gradeeditors.RestfulRegistryItem',
        'devilry.gradeeditors.ConfigEditorWindow',
        'devilry.gradeeditors.GradeEditorSelectForm',
        'devilry.extjshelpers.NotificationManager'
    ],

    /**
     * @cfg
     */
    assignmentgroupstore: undefined,

    bodyTpl: Ext.create('Ext.XTemplate',
        '<div class="section">',
        '    <tpl if="totalAssignmentGroups == 0">',
        '        <div class="section error">',
        '            <h1>No assignment groups</h1>',
        '            <p>',
        '               Students have to be organized in <em>assignment groups</em> before they can add any deliveries. A students belongs to a group even when they deliver individual deliveries. Students that is not in any assignment group do not even see the assignment. Please choose <span class="menuref">Manage assignment groups</span> to bring up the assignment group manager, and select <span class="menuref">Create groups</span>.',
        '            </p>',
        '        </div>',
        '    </tpl>',
        '    <tpl if="missingGradeEditorConfig">',
        '        <div class="section error">',
        '            <h1>Missing grade editor config</h1>',
        '            <p>',
        '                The selected grade editor, <em>{graderegistryitem.data.title}</em>, requires',
        '                configuration. Examiners will not be able to give feedback ',
        '                without a configuration, however students will be able to add deliveries.',
        '                Choose <span class="menuref">Grade editor &rarr; Configure current grade editor</span> in the toolbar to create a configuration.',
        '            </p>',
        '        </div>',
        '    </tpl>',
        '    <tpl if="graderegistryitem">',
        '        <div class="section info">',
        '            <h1>Grade editor: {graderegistryitem.data.title}</h1>',
        '            <strong>About the grade editor:</strong>',
        '            <p>',
        '                {graderegistryitem.data.description}',
        '            </p>',
        '            <strong>Why grade editors?</strong>',
        '            <p>',
        '                To make it easy for examiners to create all the information related ',
        '                to a grade, Devilry use <em>grade editors</em>. Grade editors give examiners ',
        '                a unified user-interface tailored for different kinds of grading systems.',
        '                Select <span class="menuref">Grade editor</span> in the toolbar to ',
        '                change or configure the grade editor.',
        '            </p>',
        '        </div>',
        '    </tpl>',
        '    <tpl if="published">',
        '        <div class="section info">',
        '            <h1>Published</h1>',
        '            <p>',
        '               The assignment is currently visible to students and examiners. ',
        '               Its publishing time was <strong>{publishing_time:date}</strong>.',
        '               You may change the publishing time by selecting the <span class="menuref">Edit</span> button ',
        '               in the toolbar, however since it is already published, this may lead ',
        '               to confusion among students and examiners.',
        '            </p>',
        '        </div>',
        '    </tpl>',
        '    <tpl if="!published">',
        '        <div class="section warning">',
        '             <h1>Not published</h1>',
        '             <p>',
        '                This assignment is currently <em>not visible</em> to students or examiners. ',
        '                The assignment will become visible to students and examiners ',
        '                <strong>{publishing_time:date}</strong>.',
        '                You may change the publishing time by selecting the <span class="menuref">Edit</span> button in the toolbar.',
        '             </p>',
        '        </div>',
        '    </tpl>',
        '    <tpl if="anonymous">',
        '        <div class="section info">',
        '            <h1>Anonymous</h1>',
        '            <p>',
        '                The assignment <em>is anonymous</em>. This means that examiners ',
        '                see the <em>candidate ID</em> instead of user name and ',
        '                email. Furthermore, students do not see who their examiner(s)',
        '                are. ',
        '                Select <span class="menuref">Edit</span> ',
        '                in the toolbar to change this setting.',
        '            </p>',
        '        </div>',
        '    </tpl>',
        '    <tpl if="!anonymous">',
        '        <div class="section info">',
        '            <h1>Not anonymous</h1>',
        '            <p>',
        '                The assignment is <em>not</em> anonymous. This means that examiners ',
        '                can see information about who their students are. ',
        '                Furthermore, students can see who their examiner(s)',
        '                are. This is usually OK, however on exams this is usually ',
        '                not the recommended setting. ',
        '                Select <span class="menuref">Edit</span> ',
        '                in the toolbar to change this setting.',
        '            </p>',
        '        </div>',
        '    </tpl>',
        '    <tpl if="delivery_types == 1">',
        '        <div class="section info">',
        '            <h1>Non-electronic deliveries</h1>',
        '            <p>',
        '               This assignment does not use Devilry for deliveries, only for feedback.',
        '               You may choose to use Devilry for electronic deliveries on this assignment using the <span class="menuref">Edit</span> button in the toolbar.',
        '            </p>',
        '        </div>',
        '    </tpl>',
        '</div>'
    ),

    getExtraBodyData: function(record) {
        return {
            published: record.data.publishing_time < Ext.Date.now(),
            missingGradeEditorConfig: this.missingGradeEditorConfig,
            graderegistryitem: this.gradeeditor_registryitem_recordcontainer.record,
            totalAssignmentGroups: this.assignmentgroupstore.totalCount
        };
    },

    initComponent: function() {
        this.gradeeditorconfig_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.gradeeditorconfig_recordcontainer.addListener('setRecord', this.onGradeEditorConfigLoad, this);

        this.gradeeditor_registryitem_recordcontainer= Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.gradeeditor_registryitem_recordcontainer.addListener('setRecord', this.onGradeEditorRegistryItemLoad, this);

        if(this.record) {
            this.onLoadRecord();
        } else {
            this.addListener('loadmodel', this.onLoadRecord, this);
        }

        this.studentsbutton = Ext.create('Ext.button.Button', {
            text: 'Manage assignment groups (students)',
            scale: 'large',
            listeners: {
                scope: this,
                click: this.onStudents
            }
        });

        this.selectgradeeditorbutton = Ext.widget('menuitem', {
            text: 'Change grade editor',
            scale: 'large',
            listeners: {
                scope: this,
                click: this.onSelectGradeEditorBtn,
                render: function(button) {
                    if(!this.gradeeditorconfig_recordcontainer.record) {
                        button.getEl().mask('Loading');
                    }
                }
            }
        });

        this.configuregradeeditorbutton = Ext.widget('menuitem', {
            text: 'Configure current grade editor',
            scale: 'large',
            disabled: true,
            listeners: {
                scope: this,
                click: this.onConfigureGradeEditorBtn,
                render: function(button) {
                    if(!this.gradeeditorconfig_recordcontainer.record) {
                        button.getEl().mask('Loading');
                    }
                }
            }
        });

        this.gradeeditormenu = Ext.widget('button', {
            text: 'Grade editor',
            scale: 'large',
            menu: [
                this.selectgradeeditorbutton,
                this.configuregradeeditorbutton
            ]
        });

        Ext.apply(this, {
            relatedButtons: [this.studentsbutton, this.downloadbutton = Ext.widget('button', {
                scale: 'large',
                hidden: true,
                text: 'Download all deliveries',
                listeners: {
                    scope: this,
                    click: this.onDownload
                }
            })],
            extraMeButtons: [this.gradeeditormenu],
        });
        this.callParent(arguments);
    },

    onLoadRecord: function() {
        this.checkStudents();
        Ext.ModelManager.getModel('devilry.apps.gradeeditors.simplified.administrator.SimplifiedConfig').load(this.record.data.id, {
            scope: this,
            success: function(record) {
                this.gradeeditorconfig_recordcontainer.setRecord(record);
            },
            failure: function() {
                var record = Ext.create('devilry.apps.gradeeditors.simplified.administrator.SimplifiedConfig', {
                    assignment: this.record.data.id
                });
                this.gradeeditorconfig_recordcontainer.setRecord(record);
            }
        });
        if(this.record.get('delivery_types') == 0) {
            this.downloadbutton.show();
        }
        //this.onStudents();
    },

    checkStudents: function() {
        // Load a single records to get totalCount
        this.assignmentgroupstore.pageSize = 1;
        this.assignmentgroupstore.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'parentnode',
            comp: 'exact',
            value: this.objectid
        }]);
        this.assignmentgroupstore.load({
            scope: this,
            callback: function(records, operation, success) {
                if(success) {
                    this.refreshBody();
                }
            }
        });
    },

    onGradeEditorConfigLoad: function() {
        if(this.selectgradeeditorbutton.rendered) {
            this.selectgradeeditorbutton.getEl().unmask();
        }
        this.loadGradeEditorRegistryItem();
    },

    loadGradeEditorRegistryItem: function() {
        var registryitem_model = Ext.ModelManager.getModel('devilry.gradeeditors.RestfulRegistryItem');
        this.gradeeditormenu.getEl().mask('Loading');
        registryitem_model.load(this.gradeeditorconfig_recordcontainer.record.data.gradeeditorid, {
            scope: this,
            success: function(record) {
                this.gradeeditor_registryitem_recordcontainer.setRecord(record);
            }
        });
    },

    onGradeEditorRegistryItemLoad: function() {
        var config = this.gradeeditorconfig_recordcontainer.record.data;
        var registryitem = this.gradeeditor_registryitem_recordcontainer.record.data;
        this.missingGradeEditorConfig = config.config === "" && registryitem.config_editor_url != "";
        this.refreshBody();
        this.gradeeditormenu.getEl().unmask();
        if(this.gradeeditor_registryitem_recordcontainer.record.data.config_editor_url) {
            this.configuregradeeditorbutton.enable();
        } else {
            this.configuregradeeditorbutton.disable();
        }
    },

    onSelectGradeEditorBtn: function(button) {
        var currentGradeEditorId = this.gradeeditorconfig_recordcontainer.record.data.gradeeditorid
        var editpanel = Ext.ComponentManager.create({
            xtype: 'restfulsimplified_editpanel',
            model: 'devilry.apps.gradeeditors.simplified.administrator.SimplifiedConfig',
            editform: Ext.widget('gradeeditorselectform'),
            record: this.gradeeditorconfig_recordcontainer.record,
            extrabaronbottom: true,
            beforeSave: function() {
                var config = this.record.data.config;
                if(this.down('gradeeditorselector').getValue() == currentGradeEditorId) {
                    // Clicked save without changing grade editor
                    this.up('window').close();
                    return;
                }
                if(config == null || config == '') {
                    // Do not warn when config will not be lost
                    this.doSave();
                } else {
                    Ext.MessageBox.show({
                        title: 'Confirm grade editor change',
                        msg: 'This will <strong>permanently</strong> remove your current configuration for the grade editor.',
                        buttons: Ext.Msg.YESNO,
                        icon: Ext.Msg.WARNING,
                        scope: this,
                        fn: function(btn) {
                            if(btn == 'yes') {
                                this.record.data.config = '';
                                this.doSave();
                            } else {
                                this.up('window').close();
                            }
                        }
                    });
                }
            }
        });
        var me = this;
        var editwindow = Ext.create('devilry.extjshelpers.RestfulSimplifiedEditWindowBase', {
            editpanel: editpanel,
            onSaveSuccess: function(record) {
                me.gradeeditorconfig_recordcontainer.setRecord(record);
                window.location.href = window.location.href; // TODO: Make so this hack is not needed.
                this.close();
            }
        });
        editwindow.show();
    },

    onConfigureGradeEditorBtn: function(button) {
        Ext.widget('gradeconfigeditormainwin', {
            registryitem: this.gradeeditor_registryitem_recordcontainer.record.data,
            gradeeditorconfig_recordcontainer: this.gradeeditorconfig_recordcontainer
        }).show();
    },

    onStudents: function() {
        this.hide();
        var studentswindow = Ext.widget('maximizablewindow', {
            title: Ext.create('Ext.XTemplate',
                'Manage assignment groups (students) for ',
                '{parentnode__parentnode__short_name}.',
                '{parentnode__short_name}.{short_name}'
            ).apply(this.record.data),
            width: 926,
            height: 500,
            layout: 'fit',
            maximizable: false,
            maximized: true,
            modal: true,
            onEsc: Ext.emptyFn,
            items: {
                xtype: 'administrator_studentsmanager',
                assignmentgroupstore: this.assignmentgroupstore,
                assignmentid: this.objectid,
                assignmentrecord: this.record,
                periodid: this.record.data.parentnode,
                deadlinemodel: Ext.ModelManager.getModel('devilry.apps.administrator.simplified.SimplifiedDeadline'),
                gradeeditor_config_model: Ext.ModelManager.getModel('devilry.apps.gradeeditors.simplified.administrator.SimplifiedConfig'),
                isAdministrator: true
            },
            listeners: {
                scope: this,
                close: function() {
                    this.show();
                    this.refreshBody();
                }
            }
        });
        //this.setSizeToCoverBody(studentswindow);
        studentswindow.show();
        //this.alignToCoverBody(studentswindow);
    },


    onEdit: function(button) {
        var editpanel = Ext.ComponentManager.create({
            xtype: 'restfulsimplified_editpanel',
            model: this.modelname,
            editform: Ext.widget('administrator_assignmentform'),
            record: this.record,
            saveSuccessMessage: 'Assignment successfully saved'
        });
        var editwindow = Ext.create('devilry.administrator.DefaultEditWindow', {
            editpanel: editpanel,
            prettyview: this,
            listeners: {
                scope: this,
                close: function() {
                    button.toggle(false);
                }
            }
        });
        //this.setSizeToCoverBody(editwindow);
        editwindow.show();
        //this.alignToCoverBody(editwindow);
    },

    onDownload: function() {
        window.location.href = Ext.String.format('compressedfiledownload/{0}', this.objectid);
    }
});
