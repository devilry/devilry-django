Ext.define('devilry_subjectadmin.view.passedpreviousperiod.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.passedpreviousperiodoverview',
    cls: 'devilry_subjectadmin_passedpreviousperiodoverview',
    requires: [
        //'devilry_subjectadmin.view.passedpreviousperiod.SelectAssignmentsGrid'
    ],

    /**
     * @cfg {String} assignment_id (required)
     */


    initComponent: function() {
        Ext.apply(this, {
            layout: 'card',

            items: [{
                xtype: 'container',
                itemId: 'selectAssignments',
                padding: 40,
                layout: 'border',
                items: [{
                    xtype: 'box',
                    region: 'north',
                    height: 70,
                    cls: 'bootstrap',
                    html: [
                        '<h1>',
                            gettext('Assignments:'),
                        '</h1>'
                    ].join('')
                }, {
                    //xtype: 'selectassignmentsgrid',
                    xtype: 'panel',
                    html: 'hei',
                    region: 'center',

                    fbar: ['->', {
                        xtype: 'button',
                        scale: 'large',
                        text: gettext('Next'),
                        disabled: true,
                        itemId: 'nextButton'
                    }]
                }, {
                    xtype: 'box',
                    region: 'east',
                    width: 300,
                    cls: 'bootstrap',
                    padding: '0 0 0 30',
                    html: [
                        '<p class="muted"><small>',
                            gettext('Select one or more assignments. We will search all previous semesters in this subject for assignments matching the short name of the selected assignments, and detect any students that have passing grades on those semesters.'),
                        '</small></p>'
                    ].join('')
                }]
            }, {
                xtype: 'container',
                itemId: 'selectStudents',
                padding: 40,
                items: [{
                    xtype: 'box',
                    html: 'Hello world'
                }]
            }]
        });
        this.callParent(arguments);
    }
});
