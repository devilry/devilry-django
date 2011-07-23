Ext.define('devilry.administrator.assignment.PrettyView', {
    extend: 'devilry.administrator.PrettyView',
    alias: 'widget.administrator_assignmentprettyview',

    bodyPadding: 20,

    bodyTpl: Ext.create('Ext.XTemplate',
        '<section>',
        '    <h1>{long_name} ({short_name})</h1>',
        '    <p>',
        '       The assignment is visible to students and examiners from ',
        '       <strong>{publishing_time:date}</strong>.',
        '    </p>',
        '    <tpl if="must_pass">',
        '       <h2>Must pass</h2>',
        '       <p>',
        '           Each students are <em>required</em> to get a passsing grade ',
        '           on this assigmment to pass the <em>period</em>. This requirement ',
        '           is only active for students registered on groups on this assignment.',
        '       </p>',
        '    </tpl>',
        '    <tpl if="anonymous">',
        '       <h2>Anonymous</h2>',
        '       <p>',
        '           The assignment <em>is</em> anonymous. This means that examiners ',
        '           see the <em>candidate ID</em> instead of user name and ',
        '           email. Furthermore, students do not see who their examiner(s)',
        '           are.',
        '       </p>',
        '    </tpl>',
        '    <tpl if="!anonymous">',
        '       <h2>Not anonymous</h2>',
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
                maximized: true,
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
