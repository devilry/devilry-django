/** PrettyView for an assignment. */
Ext.define('devilry.administrator.assignment.PrettyView', {
    extend: 'devilry.administrator.PrettyView',
    alias: 'widget.administrator_assignmentprettyview',
    requires: [
        'devilry.extjshelpers.studentsmanager.StudentsManager',
        'devilry.extjshelpers.RestfulSimplifiedEditPanel',
        'devilry.extjshelpers.forms.administrator.AssignmentAdvanced'
    ],

    config: {
        assignmentgroupstore: undefined
    },

    bodyTpl: Ext.create('Ext.XTemplate',
        '<section>',
        '    <tpl if="published">',
        '        <h1>Published</h1>',
        '        <p>',
        '           The assignment is currently visible to students and examiners. ',
        '           Its publishing time was <strong>{publishing_time:date}</strong>.',
        '        </p>',
        '    </tpl>',
        '    <tpl if="!published">',
        '        <section class="warning">',
        '             <h1>Not published</h1>',
        '             <p>',
        '                This assignment is currently <em>not visible</em> to students or examiners. ',
        '                The assignment will become visible to students and examiners ',
        '                <strong>{publishing_time:date}</strong>.',
        '             </p>',
        '        </section>',
        '    </tpl>',
        '    <tpl if="must_pass">',
        '       <h1>Must pass</h1>',
        '       <p>',
        '           Each students are <em>required</em> to get a passsing grade ',
        '           on this assigmment to pass the <em>period</em>. This requirement ',
        '           is only active for students registered on groups on this assignment.',
        '       </p>',
        '    </tpl>',
        '    <tpl if="anonymous">',
        '       <h1>Anonymous</h1>',
        '       <p>',
        '           The assignment <em>is anonymous</em>. This means that examiners ',
        '           see the <em>candidate ID</em> instead of user name and ',
        '           email. Furthermore, students do not see who their examiner(s)',
        '           are.',
        '       </p>',
        '    </tpl>',
        '    <tpl if="!anonymous">',
        '       <h1>Not anonymous</h1>',
        '       <p>',
        '           The assignment is <em>not</em> anonymous. This means that examiners ',
        '           can see information about who their students are. ',
        '           Furthermore, students can see who their examiner(s)',
        '           are.',
        '       </p>',
        '    </tpl>',
        '</section>'
    ),

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    getExtraBodyData: function(record) {
        return {
            published: record.data.publishing_time < Ext.Date.now(),
        };
    },

    initComponent: function() {
        this.studentsbutton = Ext.create('Ext.button.Button', {
            text: 'Students',
            scale: 'medium',
            listeners: {
                scope: this,
                click: this.onStudents
            }
        });

        this.advancedbutton = Ext.create('Ext.button.Button', {
            text: 'Advanced options',
            scale: 'medium',
            menu: [],
            listeners: {
                scope: this,
                click: this.onAdvanced
            }
        });

        Ext.apply(this, {
            relatedButtons: [this.studentsbutton],
            extraMeButtons: [this.advancedbutton],
        });
        this.callParent(arguments);
    },

    onAdvanced: function(button) {
        var editpanel = Ext.ComponentManager.create({
            xtype: 'restfulsimplified_editpanel',
            model: this.modelname,
            editform: Ext.widget('administrator_assignmentadvancedform'),
            record: this.record
        });
        var editwindow = Ext.create('devilry.administrator.DefaultEditWindow', {
            editpanel: editpanel,
            prettyview: this
        });
        editwindow.show();
        editwindow.alignTo(button, 'br', [-editwindow.getWidth(), 0]);
    },

    onStudents: function() {
        if(!this.studentswindow) {
            this.studentswindow = Ext.create('Ext.window.Window', {
                title: 'Students',
                width: 800,
                height: 600,
                layout: 'fit',
                maximizable: true,
                //maximized: true,
                closeAction: 'hide',
                items: {
                    xtype: 'studentsmanager',
                    assignmentgroupstore: this.assignmentgroupstore,
                    assignmentid: this.objectid
                },
            });
        }
        this.studentswindow.show();
    }
});
