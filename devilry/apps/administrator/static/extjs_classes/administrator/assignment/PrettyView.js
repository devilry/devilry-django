/** PrettyView for an assignment. */
Ext.define('devilry.administrator.assignment.PrettyView', {
    extend: 'devilry.administrator.PrettyView',
    alias: 'widget.administrator_assignmentprettyview',

    bodyTpl: Ext.create('Ext.XTemplate',
        '<section>',
        '    <h1>Deadline</h1>',
        '    <p>',
        '       The assignment is visible to students and examiners from ',
        '       <strong>{publishing_time:date}</strong>.',
        '    </p>',
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
        '           The assignment <em>is</em> anonymous. This means that examiners ',
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


    initComponent: function() {
        this.studentsbutton = Ext.create('Ext.button.Button', {
            text: 'Students',
            scale: 'medium',
            listeners: {
                scope: this,
                click: this.onStudents
            }
        });

        Ext.apply(this, {
            relatedButtons: [this.studentsbutton]
        });
        this.callParent(arguments);
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
                    xtype: 'box',
                    html: 'Hello world'
                },
            });
        }
        this.studentswindow.show();
    }
});
